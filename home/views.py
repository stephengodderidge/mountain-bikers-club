from django.shortcuts import render, redirect
from django.utils import timezone
from django.urls import reverse

from dashboard.forms import UserCreateForm
from trail.models import Trail


# Create your views here.
def index(request):
    form_register = UserCreateForm()
    last_trails = Trail.objects.filter(pub_date__lte=timezone.now())[:30]
    last_user_trails = Trail.objects.filter(user=request.user)[:2] if request.user.is_authenticated else None
    context = {
        'form_register': form_register,
        'last_trails': last_trails,
        'last_user_trails': last_user_trails,
    }

    return render(request, 'home/index.html', context)
