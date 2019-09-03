from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('userparts/', views.UserPartList.as_view()),
]
