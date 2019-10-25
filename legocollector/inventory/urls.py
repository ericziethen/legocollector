from django.urls import path
from django.views.generic import RedirectView

from .import views

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='userpart_list', permanent=False), name='home'),
    path('colors/', views.ColorListView.as_view(), name='color-list'),
    path('userparts/', views.UserPartListView.as_view(), name='userpart_list'),
    path('userparts/import/', views.import_userparts, name='userpart_import'),
    path('userparts/export/', views.export_userparts, name='userpart_export'),
    path('userparts/new/', views.FilteredPartListUserPartCreateView.as_view(), name='userpart_create'),
    path('userparts/<int:pk1>/delete/', views.UserPartDeleteView.as_view(), name='userpart_delete'),
    path('userparts/<int:pk1>/edit/', views.UserPartUpdateView.as_view(), name='userpart_edit'),
    path('userparts/<int:pk1>/colors/', views.UserPartManageColorsView.as_view(), name='userpart_colors'),
    path('userparts/<int:pk1>/', views.UserPartDetailView.as_view(), name='userpart_detail'),

    # path('userparts/<int:pk1>/inventory/', views.UserPartInventoryListView.as_view(), name='inventory_list'),
    path('userparts/<int:pk1>/inventory/new/', views.InventoryCreateView.as_view(), name='inventory_create'),
    path('userparts/<int:pk1>/inventory/<int:pk2>/delete/', views.InventoryDeleteView.as_view(), name='inventory_delete'),  # pylint:disable=line-too-long
    path('userparts/<int:pk1>/inventory/<int:pk2>/edit/', views.InventoryUpdateView.as_view(), name='inventory_edit'),
    path('userparts/<int:pk1>/inventory/<int:pk2>/', views.InventoryDetailView.as_view(), name='inventory_detail'),
    path('ajax/convert_color_id_to_rgb/', views.convert_color_id_to_rgb, name='convert_color_id_to_rgb'),
]
