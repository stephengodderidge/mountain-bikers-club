import io

from django.conf import settings
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.contrib.sites.models import Site
from staticmap import StaticMap, Line

from mountainbikers.celery import app
from .utils.gpx import get_coordinates, parse
from shell.utils.mail import mail


@app.task
def create_thumbnail(trail_id, points, width, height):
    from .models import Trail
    current_site = Site.objects.get_current()

    h = 'http' if settings.DEBUG else 'https'

    coordinates = get_coordinates(points)
    m = StaticMap(int(width), int(height), 10, 10, h + '://' + current_site.domain + '/trail/api/tile/{z}/{x}/{y}.png')
    m.add_line(Line(coordinates, 'white', 11))
    m.add_line(Line(coordinates, '#2E73B8', 5))
    image = m.render()
    f = io.BytesIO(b'')
    image.save(f, format='JPEG', optimize=True, progressive=True)

    trail = Trail.objects.get(pk=trail_id)
    trail.thumbnail.delete(save=False)
    trail.thumbnail.save('thumbnail.jpg', f)

    to = mail(
        trail.name,
        'You\'re trail is ready.\n' +
        'https://mountainbikers.club' +
        reverse('trail__main', args=[trail.id])
    )
    to([trail.author.email])

@app.task
def parse_gpx(trail_id):
    from .models import Trail

    trail = Trail.objects.get(pk=trail_id)

    if bool(trail.file):
        with trail.file.open() as file:
            gpx_file = file.read()
            name, description, tracks = parse(gpx_file.decode('utf-8'))

            first_track = tracks[0]

            # FIXME gettext doesn't seem to work
            trail.name = name or first_track['name'] or _('Unnamed Trail')
            trail.description = description or first_track['description'] or None
            trail.tracks = tracks
            # TODO Change the pub_date (or set it up). Remove it from view.
            trail.save()
            # TODO Send an email to notify the user the work is done.

            # Asynchronous Thumbnail
            create_thumbnail.delay(trail.id, first_track['points'], 425, 225)
