from django.urls import path

from . import views


urlpatterns = [
    path('new/', views.new, name='trail__new'),
    path('<uuid:trail_id>/edit/', views.edit, name='trail__edit'),
    path('<uuid:trail_id>/delete/', views.delete, name='trail__delete'),
    path('<uuid:trail_id>/favorite/', views.favorite, name='trail__favorite'),
    path('<uuid:trail_id>/', views.main, name='trail__main'),
    path('api/<uuid:trail_id>/track/<int:track_id>', views.track_json, name="trail__track_points"),
]
