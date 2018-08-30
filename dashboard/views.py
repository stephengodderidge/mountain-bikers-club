from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.urls import reverse

from .forms import UserCreateForm, UserProfileForm
from trail.models import Trail


# Create your views here.
@login_required
def index(request):
    user_trails = Trail.objects.filter(user=request.user)
    context = {
        'user_trails': user_trails
    }

    return render(request, 'dashboard/index.html', context)


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

            return HttpResponseRedirect(reverse('profile'))

    else:
        form = UserCreateForm()

    context = {
        'form': form,
    }

    return render(request, 'dashboard/register.html', context)


@login_required
def profile(request):
    current_user = request.user

    if request.method == 'POST':
        form = UserProfileForm(data=request.POST, instance=current_user)

        if form.is_valid():
            form.save()

            return HttpResponseRedirect(reverse('dashboard'))

    else:
        form = UserProfileForm(instance=current_user)

    context = {
        'form': form,
    }

    return render(request, 'dashboard/profile.html', context)


@login_required
def delete(request):
    current_user = request.user
    current_user.delete()

    return HttpResponseRedirect(reverse('home'))
