from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required

from trail.models import Trail
from .models import User
from .forms import UserCreateForm, UserProfileForm


def main(request, username):
    member = get_object_or_404(User, username=username)
    member_trails = Trail.objects.filter(author=member)
    member_favorite_trails = Trail.objects.filter(favorite_by=member)
    context = {
        'member': member,
        'member_trails': member_trails,
        'member_favorite_trails': member_favorite_trails,
    }

    return render(request, 'member/main.html', context)


def register(request):
    if request.method == 'POST':
        form = UserCreateForm(request.POST)

        if form.is_valid():
            user = User.objects.create_user(
                request.POST['username'],
                request.POST['email'],
                request.POST['password1']
            )
            user.save()

            return HttpResponseRedirect(reverse('member__edit'))

    else:
        form = UserCreateForm()

    context = {
        'form': form,
    }

    return render(request, 'member/register.html', context)


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

    return render(request, 'member/edit.html', context)


@login_required
def delete(request):
    current_user = request.user
    current_user.delete()

    return HttpResponseRedirect(reverse('home'))
