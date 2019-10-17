from django.contrib import admin

from .models import PartRelationship, Color, Part, PartCategory, UserPart, Inventory


class ColorAdmin(admin.ModelAdmin):
    fields = ['name', 'transparent', 'rgb']
    list_display = ('name', 'rgb', 'transparent')
    search_fields = ['name']


class PartAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Identification', {'fields': ['part_num', 'name', 'category_id']}),
        ('Dimensions', {'fields': ['width', 'height', 'length']}),
    ]
    list_display = ('part_num', 'name', 'category_id', 'width', 'height', 'length', 'id')
    list_filter = ['width', 'height', 'length']
    search_fields = ['part_num', 'name', 'category_id__name']


class UserPartAdmin(admin.ModelAdmin):
    list_display = ('user', 'part')


class InventoryAdmin(admin.ModelAdmin):
    list_display = ('userpart', 'color', 'qty')


# Register your models here.
admin.site.register(PartRelationship)
admin.site.register(Color, ColorAdmin)
admin.site.register(Part, PartAdmin)
admin.site.register(PartCategory)
admin.site.register(UserPart, UserPartAdmin)
admin.site.register(Inventory, InventoryAdmin)
