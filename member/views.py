from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404

from trail.models import Trail


def main(request, username):
    member = get_object_or_404(User, username=username)
    member_trails = Trail.objects.filter(user=member)
    context = {
        'member': member,
        'member_trails': member_trails,
    }

    return render(request, 'member/main.html', context)
