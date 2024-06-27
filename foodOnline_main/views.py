from django.shortcuts import render
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D # For distance
from django.contrib.gis.db.models.functions import Distance

from vendor.models import Vendor


def get_or_set_current_location(request):
    if "lat" in request.session:
        lat = request.session["lat"]
        lng = request.session["lng"]
        return lat, lng
    elif "lat" in request.GET:
        lat = request.GET.get("lat")
        lng = request.GET.get("lng")
        request.session["lat"] = lat
        request.session["lng"] = lng
        return lat, lng
    else:
        return None


def home(request):
    location = get_or_set_current_location(request)
    if location is not None:
        lat, lng = location
        pnt = GEOSGeometry(f"POINT({lng} {lat})")

        vendors = Vendor.objects.filter(
            user_profile__location__distance_lte=(pnt, D(km=20))
        ).annotate(distance=Distance("user_profile__location", pnt)).order_by("distance")

        for v in vendors:
            v.kms = round(v.distance.km, 1)
    else:
        vendors = Vendor.objects.filter(is_approved=True, user__is_active=True)[:8]
    context = {
        'vendors': vendors
    }
    return render(request, 'home.html', context)
