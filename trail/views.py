import os

import requests
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse, Http404, HttpResponse
from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from .forms import GpxUploadForm, GpxEditForm
from .models import Trail
from .tasks import parse_gpx


@login_required
def new(request):
    current_user = request.user

    if request.method == 'POST':
        form = GpxUploadForm(data=request.POST, files=request.FILES)

        if form.is_valid():
            f = form.save(commit=False)
            f.author = current_user
            f.pub_date = timezone.now()
            f.save()
            parse_gpx.delay(f.id)

            return HttpResponseRedirect(reverse('trail__main', args=[f.id]))

    else:
        form = GpxUploadForm()

    context = {
        'form': form,
    }

    return render(request, 'trail/new.html', context)


@login_required
def edit(request, trail_id):
    trail = get_object_or_404(Trail, pk=trail_id, author=request.user)

    if request.method == 'POST':
        form = GpxEditForm(data=request.POST, instance=trail)

        if form.is_valid():
            form.save()

            return HttpResponseRedirect(reverse('trail__main', args=[trail.id]))

    else:
        form = GpxEditForm(instance=trail)

    context = {
        'form': form,
        'trail': trail,
    }

    return render(request, 'trail/edit.html', context)


@login_required
def favorite(request, trail_id):
    current_user = request.user
    current_user_favorite_trails = current_user.favorite_trails.all()
    trail = get_object_or_404(Trail, pk=trail_id)

    if trail in current_user_favorite_trails:
        current_user.favorite_trails.remove(trail)
    else:
        current_user.favorite_trails.add(trail)

    return HttpResponseRedirect(reverse('trail__main', args=[trail.id]))


@login_required
def delete(request, trail_id):
    current_trail = get_object_or_404(Trail, pk=trail_id)
    current_trail.delete()

    return HttpResponseRedirect(reverse('dashboard__main'))


def main(request, trail_id):
    current_user = request.user
    trail = get_object_or_404(Trail, pk=trail_id)
    is_favorite = False

    if current_user.is_authenticated:
        is_favorite = current_user in trail.favorite_by.all()

    context = {
        'trail': trail,
        'is_favorite': is_favorite,
    }

    return render(request, 'trail/main.html', context)


def track_json(request, trail_id, track_id):
    trail = get_object_or_404(Trail, pk=trail_id)
    try:
        points = trail.tracks[track_id] or {}
    except IndexError:
        raise Http404("Track index is out of range")

    return JsonResponse(points, safe=False)


def tile(request, z, x, y):
    # Fallback to OpenCycleMap
    urlTopo = 'https://b.tile.opentopomap.org/{}/{}/{}.png'.format(z, x, y)
    urlCycle = 'https://tile.thunderforest.com/cycle/{}/{}/{}.png?apikey={}'.format(z, x, y, os.environ.get('OPEN_CYCLE_MAP'))
    r = requests.get(urlTopo, timeout=60)
    if r.status_code != 200:
        r = requests.get(urlCycle)

    return HttpResponse(r.content, content_type='image/png')
