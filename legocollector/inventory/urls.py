from django.urls import path
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    path('userparts/', views.UserPartListView.as_view(), name='home'),
    path('userparts/new', views.UserPartCreateView.as_view(), name='userpart_create'),
    path('userparts/<int:pk>/delete', views.UserPartDeleteView.as_view(), name='userpart_delete'),
    path('userparts/<int:pk>/edit', views.UserPartUpdateView.as_view(), name='userpart_edit'),
    path('userparts/<int:pk>/', views.UserPartDetailView.as_view(), name='userpart_detail'),
    path('', RedirectView.as_view(pattern_name='home', permanent=False)),
]
