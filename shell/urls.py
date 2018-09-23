from django.urls import path

from . import views

urlpatterns = [
    path('bokeh.js', views.bokeh_js, name='bokeh__js'),
    path('bokeh.css', views.bokeh_css, name='bokeh__css'),
]
