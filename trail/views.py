import os
import requests
from bokeh.models import Range1d, LinearAxis, PrintfTickFormatter

from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse, Http404, HttpResponse
from django.urls import reverse, reverse_lazy
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.utils.translation import gettext as _
from bokeh.plotting import figure
from bokeh.embed import components
from django.views.generic import DeleteView
from scipy.signal import savgol_filter

from .forms import GpxUploadForm, GpxEditForm
from .models import Trail
from .tasks import parse_gpx


@login_required
def new(request):
    current_user = request.user
    base_uri = request.scheme + '://' + request.get_host()

    if request.method == 'POST':
        form = GpxUploadForm(data=request.POST, files=request.FILES)

        if form.is_valid():
            f = form.save(commit=False)
            f.author = current_user
            f.pub_date = timezone.now()
            f.save()
            parse_gpx.delay(f.id, base_uri)

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


class TrailDelete(DeleteView):
    success_url = reverse_lazy('dashboard__main')
    model = Trail

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(author=self.request.user)


def main(request, trail_id):
    current_user = request.user
    trail = get_object_or_404(Trail, pk=trail_id)
    is_favorite = False
    charts = []

    if trail.is_private and not (current_user.is_authenticated and trail.author == current_user):
        raise Http404(_('Trail does not exist'))

    if current_user.is_authenticated:
        is_favorite = current_user in trail.favorite_by.all()

    # Chart
    if trail.tracks is not None and len(trail.tracks) > 0:
        for track in trail.tracks:
            x_distance = list(map(lambda p: p['total_distance'], track['points']))
            y_elevation = list(map(lambda p: p['elevation'], track['points']))
            y_speed = list(map(lambda p: p['speed'], track['points']))

            plot = figure(
                tools='crosshair,pan,wheel_zoom,box_zoom,reset,save',
                toolbar_location='above',
                sizing_mode='scale_width',
                plot_width=1100,
                plot_height=400,
            )

            plot.y_range = Range1d(start=min(y_elevation) - 30, end=max(y_elevation) + 30)
            plot.extra_y_ranges['speed'] = Range1d(start=min(y_speed), end=max(y_speed) + 3)
            plot.add_layout(LinearAxis(y_range_name='speed'), 'right')

            plot.line(x_distance, y_elevation, legend=_('Elevation'), line_width=3, color='#3d85cc')
            plot.line(x_distance, savgol_filter(y_speed, 101, 9), legend=_('Speed'), line_width=1,
                      y_range_name='speed', color='#66cc66')

            plot.xaxis[0].formatter = PrintfTickFormatter(format='%4.0d km')
            plot.yaxis[0].formatter = PrintfTickFormatter(format='%5.0d m')
            plot.yaxis[1].formatter = PrintfTickFormatter(format='%3.0d km/h')

            # Styling
            # http://bokeh.pydata.org/en/latest/docs/user_guide/styling.html
            plot.border_fill_color = '#2d2d2d'
            plot.background_fill_color = '#393939'

            plot.outline_line_color = 'black'

            plot.xaxis.major_label_text_color = '#d3d0c8'
            plot.xaxis.axis_label_text_color = '#d3d0c8'
            plot.yaxis[0].major_label_text_color = '#3d85cc'
            plot.yaxis[0].axis_label_text_color = '#3d85cc'
            plot.yaxis[1].major_label_text_color = '#66cc66'
            plot.yaxis[1].axis_label_text_color = '#66cc66'

            plot.xgrid.grid_line_color = '#515151'
            plot.xgrid.grid_line_dash = [6, 4]
            plot.ygrid.grid_line_color = '#515151'
            plot.ygrid.grid_line_dash = [6, 4]

            plot.xgrid.minor_grid_line_color = '#515151'
            plot.xgrid.minor_grid_line_alpha = 0.5
            plot.xgrid.minor_grid_line_dash = [6, 4]
            plot.ygrid.minor_grid_line_color = '#515151'
            plot.ygrid.minor_grid_line_alpha = 0.5
            plot.ygrid.minor_grid_line_dash = [6, 4]

            plot.title.text_color = '#a09f93'

            plot.legend.location = 'top_left'
            # plot.legend.orientation = 'horizontal'
            plot.legend.label_text_color = '#a09f93'
            plot.legend.border_line_color = '#515151'
            plot.legend.background_fill_color = '#2d2d2d'
            plot.legend.background_fill_alpha = 0.85
            plot.legend.click_policy = 'hide'
            plot.legend.inactive_fill_color = '#2d2d2d'

            script, div = components(plot)

            charts.append({
                'script': script,
                'div': div,
            })

    context = {
        'trail': trail,
        'is_favorite': is_favorite,
        'charts': charts,
    }

    return render(request, 'trail/main.html', context)


def track_json(request, trail_id, track_id):
    current_user = request.user
    trail = get_object_or_404(Trail, pk=trail_id)

    if trail.is_private and not (current_user.is_authenticated and trail.author == current_user):
        raise Http404(_('Trail does not exist'))

    try:
        points = trail.tracks[track_id] or {}
    except IndexError:
        raise Http404(_('Track index is out of range'))

    return JsonResponse(points, safe=False)


def tile(request, z, x, y):
    url_komoot = 'http://a.tile.komoot.de/komoot-2/{}/{}/{}.png'.format(z, x, y)
    url_topo = 'https://b.tile.opentopomap.org/{}/{}/{}.png'.format(z, x, y)
    url_cycle = 'https://tile.thunderforest.com/cycle/{}/{}/{}.png?apikey={}'\
        .format(z, x, y, os.environ.get('OPEN_CYCLE_MAP'))

    r = requests.get(url_komoot, timeout=60)
    if r.status_code != 200:
        r = requests.get(url_topo, timeout=60)
    if r.status_code != 200:
        r = requests.get(url_cycle, timeout=60)

    return HttpResponse(r.content, content_type='image/png')
