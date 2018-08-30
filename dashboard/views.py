from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from trail.models import Trail


@login_required
def main(request):
    user_trails = Trail.objects.filter(user=request.user)
    context = {
        'user_trails': user_trails
    }

    return render(request, 'dashboard/index.html', context)
