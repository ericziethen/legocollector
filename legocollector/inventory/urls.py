from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html')),
    #path('', views.index, name='home'),
    path('userparts/', views.UserPartList.as_view()),
]
