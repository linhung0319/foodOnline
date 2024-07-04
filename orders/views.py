import json

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.sites.shortcuts import get_current_site

from menu.models import FoodItem
from marketplace.models import Cart, Tax
from marketplace.context_processors import get_cart_amounts
from accounts.utils import send_notification
from .forms import OrderForm
from .models import Order, Payment, OrderedFood
from .utils import generate_order_number


@login_required(login_url="accounts:login")
def place_order(request):
    cart_items = Cart.objects.filter(user=request.user).order_by("created_at")
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect("marketplace:marketplace")
    
    vendors_ids = []
    for i in cart_items:
        if i.fooditem.vendor.id not in vendors_ids:
            vendors_ids.append(i.fooditem.vendor.id)
    
    get_tax = Tax.objects.filter(is_active=True)
    x = {} # {"vendor_id": subtotal}
    for i in cart_items:
        fooditem = FoodItem.objects.get(pk=i.fooditem.id, vendor_id__in=vendors_ids)
        v_id = fooditem.vendor.id
        if v_id in x:
            x[v_id] += (fooditem.price * i.quantity)
        else:
            x[v_id] = (fooditem.price * i.quantity)

    # Calculate the tax_data for each vendor
    # {"vendor_id": {"subtotal": {"tax_type": {"tax_percentage": "tax_amount"}}}}
    total_data = {}
    for v_id, subtotal in x.items():
        tax_dict = {}
        for j in get_tax:
            tax_type = j.tax_type
            tax_percentage = j.tax_percentage
            tax_amount = round((tax_percentage * subtotal) / 100, 2)
            tax_dict.update({tax_type: {str(tax_percentage): str(tax_amount)}})
        total_data.update({v_id: {str(subtotal): tax_dict}})

    cart_amounts = get_cart_amounts(request)
    subtotal = cart_amounts["subtotal"]
    total_tax = cart_amounts["tax"]
    grand_total = cart_amounts["grand_total"]
    tax_data = cart_amounts["tax_dict"]

    if request.method == "POST":
        form = OrderForm(request.POST)
        if form.is_valid():
            order = Order()
            order.first_name = form.cleaned_data["first_name"]
            order.last_name = form.cleaned_data["last_name"]
            order.phone = form.cleaned_data["phone"]
            order.email = form.cleaned_data["email"]
            order.address = form.cleaned_data["address"]
            order.country = form.cleaned_data["country"]
            order.state = form.cleaned_data["state"]
            order.city = form.cleaned_data["city"]
            order.pin_code = form.cleaned_data["pin_code"]
            order.user = request.user
            order.total = grand_total
            order.tax_data = json.dumps(tax_data)
            order.total_data = json.dumps(total_data)
            order.total_tax = total_tax
            order.payment_method = request.POST["payment_method"]
            order.save() # order id is generated here
            order.order_number = generate_order_number(order.id)
            order.vendors.add(*vendors_ids)
            order.save()
            context = {
                "order": order,
                "cart_items": cart_items,
            }
            return render(request, "orders/place_order.html", context)
        else:
            print(form.errors)

    return render(request, "orders/place_order.html")


@login_required(login_url="accounts:login")
def payments(request):
    # Check if the request is ajax or not
    if request.headers.get("x-requested-with") == "XMLHttpRequest" and request.method == "POST":
        # Store the payment details in the payment model
        order_number = request.POST.get("order_number")
        transaction_id = request.POST.get("transaction_id")
        payment_method = request.POST.get("payment_method")
        status = request.POST.get("status")
        
        order = Order.objects.get(user=request.user, order_number=order_number)
        payment = Payment(
            user=request.user,
            transaction_id = transaction_id,
            payment_method = payment_method,
            amount = order.total,
            status = status,
        )
        payment.save()

        # Update the order model
        order.payment = payment
        order.is_ordered = True
        order.save()

        # Move the cart items to ordered food model
        cart_items = Cart.objects.filter(user=request.user)
        for item in cart_items:
            ordered_food = OrderedFood()
            ordered_food.order = order
            ordered_food.payment = payment
            ordered_food.user = request.user
            ordered_food.fooditem = item.fooditem
            ordered_food.quantity = item.quantity
            ordered_food.price = item.fooditem.price
            ordered_food.amount = item.fooditem.price * item.quantity # total amount
            ordered_food.save()  

        # Send order confirmation email to the customer
        mail_subject = "Thank you for ordering with us."
        mail_template = "orders/order_confirmation_email.html"

        ordered_foods = OrderedFood.objects.filter(order=order)
        customer_subtotal = 0
        for item in ordered_foods:
            customer_subtotal += (item.price * item.quantity)
        tax_data = json.loads(order.tax_data)

        context = {
            "user": request.user,
            "order": order,
            "to_email": order.email,
            "ordered_foods": ordered_foods,
            "domain": get_current_site(request),
            "customer_subtotal": customer_subtotal,
            "tax_data": tax_data,
        }
        send_notification(mail_subject, mail_template, context)

        # Send order received email to the vendor
        mail_subject = "You have received a new order."
        mail_template = "orders/new_order_received.html"
        to_emails = []
        for i in cart_items:
            if i.fooditem.vendor.user.email not in to_emails:
                to_emails.append(i.fooditem.vendor.user.email)

                ordered_food_to_vendor = OrderedFood.objects.filter(order=order, fooditem__vendor=i.fooditem.vendor)
                order_data = order.get_total_by_vendor(i.fooditem.vendor.user)
                
                context = {
                    "order": order,
                    "to_email": i.fooditem.vendor.user.email,
                    "ordered_food_to_vendor": ordered_food_to_vendor,
                    "order_data": order_data,
                }
                send_notification(mail_subject, mail_template, context)

        # Clear the cart if the payment is success
        cart_items.delete()

        # Return back to AJAX with the status success or failure
        response = {
            "order_number": order_number,
            "transaction_id": transaction_id,
        }
        return JsonResponse(response)
    return HttpResponse("Payments")


def order_complete(request):
    order_number = request.GET.get("order_no")
    transaction_id = request.GET.get("trans_id")
    
    try:
        order = Order.objects.get(
            order_number=order_number, 
            payment__transaction_id=transaction_id,
            is_ordered=True,
        )
        ordered_food = OrderedFood.objects.filter(order=order)

        subtotal = 0
        for item in ordered_food:
            subtotal += (item.price * item.quantity)
        
        tax_data = json.loads(order.tax_data)

        context = {
            "order": order,
            "ordered_food": ordered_food,
            "subtotal": subtotal,
            "tax_data": tax_data
        }
        return render(request, "orders/order_complete.html", context)
    except:
        return redirect("home")
    