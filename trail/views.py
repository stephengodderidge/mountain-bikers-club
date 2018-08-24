from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from .forms import GpxUploadForm, GpxEditForm
from .models import Trail


# Create your views here.
@login_required
def upload(request):
    current_user = request.user

    if request.method == 'POST':
        form = GpxUploadForm(data=request.POST, files=request.FILES)

        if form.is_valid():
            f = form.save(commit=False)
            f.user = current_user
            f.pub_date = timezone.now()
            f.save()

            return HttpResponseRedirect(reverse('trail__edit', args=[f.id]))

    else:
        form = GpxUploadForm()

    context = {
        'form': form,
    }

    return render(request, 'trail/upload.html', context)


def view(request, trail_id):
    trail = get_object_or_404(Trail, pk=trail_id)
    context = {
        'trail': trail
    }

    return render(request, 'trail/view.html', context)


@login_required
def edit(request, trail_id):
    trail = get_object_or_404(Trail, pk=trail_id, user=request.user)

    if request.method == 'POST':
        form = GpxEditForm(data=request.POST, instance=trail)

        if form.is_valid():
            form.save()

            return HttpResponseRedirect(reverse('trail', args=[trail.id]))

    else:
        form = GpxEditForm(instance=trail)

    context = {
        'form': form,
        'trail': trail,
    }

    return render(request, 'trail/edit.html', context)


@login_required
def delete(request, trail_id):
    current_trail = get_object_or_404(Trail, pk=trail_id)
    current_trail.delete()

    # FIXME (do remove empty folders via a 'cron' task)
    # trail_path = os.path.join(settings.MEDIA_ROOT, 'trails/', str(trail_id))
    # if os.path.isdir(trail_path):
    #     shutil.rmtree(trail_path)

    return HttpResponseRedirect(reverse('dashboard'))
