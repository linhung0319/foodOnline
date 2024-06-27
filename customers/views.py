from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from accounts.forms import UserProfileForm, UserInfoForm
from accounts.models import UserProfile


@login_required(login_url="login")
def cprofile(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    if request.method == "POST":
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)
        user_form = UserInfoForm(request.POST, instance=request.user)
        if profile_form.is_valid() and user_form.is_valid():
            profile_form.save()
            user_form.save()
            messages.success(request, "Profile Updated")
            return redirect("accounts:customers:cprofile")
        else:
            print(profile_form.errors)
            print(user_form.errors)
    else:
        user_form = UserInfoForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)
    
    context = {
        "user_form": user_form,
        "profile_form": profile_form,
        "profile": profile,
    }
    return render(request, "customers/cprofile.html", context)