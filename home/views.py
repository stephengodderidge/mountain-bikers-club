from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from trail.models import Trail
from .forms import UserCreateForm, UserProfileForm


# Create your views here.
def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('dashboard__main'))

    form_register = UserCreateForm()
    context = {
        'form_register': form_register,
    }

    return render(request, 'home/index.html', context)


def register(request):
    if request.method == 'POST':
        form = UserCreateForm(request.POST)

        if form.is_valid():
            user = User.objects.create_user(
                request.POST['username'],
                None,
                request.POST['password1']
            )
            user.save()

            return HttpResponseRedirect(reverse('member__edit'))

    else:
        form = UserCreateForm()

    context = {
        'form': form,
    }

    return render(request, 'home/register.html', context)


@login_required
def edit(request):
    current_user = request.user

    if request.method == 'POST':
        form = UserProfileForm(data=request.POST, instance=current_user)

        if form.is_valid():
            form.save()

            return HttpResponseRedirect(reverse('member__main', None, args=[current_user.username]))

    else:
        form = UserProfileForm(instance=current_user)

    context = {
        'form': form,
    }

    return render(request, 'home/edit.html', context)


@login_required
def delete(request):
    current_user = request.user
    current_user.delete()

    return HttpResponseRedirect(reverse('home'))


def discover(request):
    last_trails = Trail.objects.filter(pub_date__lte=timezone.now())[:30]
    context = {
        'last_trails': last_trails,
    }

    return render(request, 'home/discover.html', context)
