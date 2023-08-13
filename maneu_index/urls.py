from django.urls import path

from maneu_index import views

app_name = 'maneu_index'
urlpatterns = [
    # views
    path('', views.index, name='index'),
]
