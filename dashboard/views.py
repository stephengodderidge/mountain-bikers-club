from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from trail.models import Trail


@login_required
def main(request):
    last_user_trails = Trail.objects.filter(author=request.user)[:3]
    context = {
        'last_user_trails': last_user_trails
    }

    return render(request, 'dashboard/index.html', context)
