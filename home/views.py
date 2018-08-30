from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
from django.urls import reverse

from dashboard.forms import UserCreateForm
from trail.models import Trail


# Create your views here.
def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('dashboard'))

    form_register = UserCreateForm()
    context = {
        'form_register': form_register,
    }

    return render(request, 'home/index.html', context)


def discover(request):
    last_trails = Trail.objects.filter(pub_date__lte=timezone.now())[:30]
    context = {
        'last_trails': last_trails,
    }

    return render(request, 'home/discover.html', context)
