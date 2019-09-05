from django.urls import path
from django.views.generic import TemplateView

from . import views

urlpatterns = [
    path('', TemplateView.as_view(template_name='index.html')),
    path('userparts/new', views.UserPartCreateView.as_view(), name='userpart_create'),
    path('userparts/', views.UserPartListView.as_view(), name='userpart_list'),
    path('userparts/<int:pk>/delete', views.UserPartDeleteView.as_view(), name='userpart_delete'),
    path('userparts/<int:pk>/edit', views.UserPartUpdateView.as_view(), name='userpart_edit'),
    path('userparts/<int:pk>/', views.UserPartDetailView.as_view(), name='userpart_detail'),
]
