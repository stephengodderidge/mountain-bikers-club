from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
from django.urls import reverse
from django.views.decorators.cache import cache_page

from trail.models import Trail
from member.forms import UserCreateForm


@cache_page(60 * 60 * 24)
def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('dashboard__main'))

    form_register = UserCreateForm()
    context = {
        'form_register': form_register,
    }

    return render(request, 'discover/index.html', context)


@cache_page(60 * 15)
def discover(request):
    current_user = request.user
    last_trails = Trail.objects.filter(pub_date__lte=timezone.now(), is_draft=False)

    if current_user.is_authenticated:
        last_trails = last_trails.exclude(author=current_user)

    context = {
        'last_trails': last_trails[:30],
    }

    return render(request, 'discover/discover.html', context)
