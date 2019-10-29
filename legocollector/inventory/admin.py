from django.contrib import admin

from .models import (
    Color, Part, PartCategory, PartRelationship,
    PartExternalId, SetPart, UserPart, Inventory
)


class ColorAdmin(admin.ModelAdmin):
    fields = ['name', 'transparent', 'rgb']
    list_display = ('name', 'rgb', 'transparent')
    search_fields = ['name']


class PartAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Identification', {'fields': ['part_num', 'name', 'category']}),
        ('Dimensions', {'fields': ['width', 'height', 'length']}),
        ('Available Colors', {'fields': ['available_colors']}),
        ('Related parts', {'fields': ['related_parts']}),
    ]
    list_display = ('part_num', 'name', 'category', 'width', 'height', 'length',
                    'id', 'related_part_count')
    list_filter = ['width', 'height', 'length']
    search_fields = ['part_num', 'name', 'category__name']
    readonly_fields = ['related_parts', 'available_colors']

    def related_parts(self, obj):  # pylint:disable=no-self-use
        return ', '.join(p.part_num for p in obj.get_related_parts(
            parents=True, children=True, transitive=True))

    def related_part_count(self, obj):  # pylint:disable=no-self-use
        return F'{obj.related_part_count(parents=True, children=True, transitive=True)}'

    def available_colors(self, obj):  # pylint:disable=no-self-use
        return ', '.join(c.name for c in obj.available_colors.order_by('name'))


class SetPartAdmin(admin.ModelAdmin):
    list_display = ('set_inventory', 'part', 'color', 'qty', 'is_spare')


class PartExternalIdpAdmin(admin.ModelAdmin):
    list_display = ('part', 'provider', 'external_id')


class PartRelationshipAdmin(admin.ModelAdmin):
    list_display = ('parent_part', 'child_part')


class UserPartAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Colors', {'fields': ['used_colors', 'unused_colors']}),
    ]
    list_display = ('user', 'part', 'used_colors', 'unused_colors')
    readonly_fields = ['used_colors', 'unused_colors']

    def used_colors(self, obj):  # pylint:disable=no-self-use
        return ', '.join(c.name for c in obj.used_colors.order_by('name'))

    def unused_colors(self, obj):  # pylint:disable=no-self-use
        return ', '.join(c.name for c in obj.unused_colors.order_by('name'))

class InventoryAdmin(admin.ModelAdmin):
    list_display = ('userpart', 'color', 'qty')


# Register your models here.
admin.site.register(Color, ColorAdmin)
admin.site.register(Part, PartAdmin)
admin.site.register(SetPart, SetPartAdmin)
admin.site.register(PartCategory)
admin.site.register(PartRelationship, PartRelationshipAdmin)
admin.site.register(PartExternalId, PartExternalIdpAdmin)
admin.site.register(UserPart, UserPartAdmin)
admin.site.register(Inventory, InventoryAdmin)
