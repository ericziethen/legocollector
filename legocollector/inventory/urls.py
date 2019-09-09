from django.urls import path
from django.views.generic import RedirectView

from .import views

urlpatterns = [
    path('userparts/', views.UserPartListView.as_view(), name='home'),
    path('userparts/import/', views.import_userparts, name='userpart_import'),
    path('userparts/export/', views.export_userparts, name='userpart_export'),
    path('userparts/new/', views.UserPartCreateView.as_view(), name='userpart_create'),
    path('userparts/<int:pk1>/delete/', views.UserPartDeleteView.as_view(), name='userpart_delete'),
    path('userparts/<int:pk1>/edit/', views.UserPartUpdateView.as_view(), name='userpart_edit'),
    path('userparts/<int:pk1>/', views.UserPartDetailView.as_view(), name='userpart_detail'),

    #path('userparts/<int:pk1>/inventory/', views.UserPartInventoryListView.as_view(), name='inventory_list'),   # DO WE NEED THIS AS OVERALL LIST???
    path('userparts/<int:pk1>/inventory/new/', views.InventoryCreateView.as_view(), name='inventory_create'),
    path('userparts/<int:pk1>/inventory/<int:pk2>/delete/', views.InventoryDeleteView.as_view(), name='inventory_delete'),
    path('userparts/<int:pk1>/inventory/<int:pk2>/edit/', views.InventoryUpdateView.as_view(), name='inventory_edit'),
    path('userparts/<int:pk1>/inventory/<int:pk2>/', views.InventoryDetailView.as_view(), name='inventory_detail'),
    path('', RedirectView.as_view(pattern_name='home', permanent=False)),
]
