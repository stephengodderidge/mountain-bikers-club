from django.urls import path
from django.contrib.auth.decorators import login_required

from .views import TrailDelete
from . import views


urlpatterns = [
    path('new/', views.new, name='trail__new'),
    path('<uuid:trail_id>/edit/', views.edit, name='trail__edit'),
    path('<pk>/delete/', login_required(TrailDelete.as_view()), name='trail__delete'),
    path('<uuid:trail_id>/favorite/', views.favorite, name='trail__favorite'),
    path('<uuid:trail_id>/', views.main, name='trail__main'),
    path('api/<uuid:trail_id>/track/<int:track_id>', views.track_json, name="trail__track_points"),
    path('api/tile/<int:z>/<int:x>/<int:y>.png', views.tile),
]
