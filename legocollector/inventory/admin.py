from django.contrib import admin

from .models import (
    Color, Part, PartCategory, PartRelationship,
    PartExternalId, UserPart, Inventory
)


class ColorAdmin(admin.ModelAdmin):
    fields = ['name', 'transparent', 'rgb']
    list_display = ('name', 'rgb', 'transparent')
    search_fields = ['name']


class PartAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Identification', {'fields': ['part_num', 'name', 'category']}),
        ('Dimensions', {'fields': ['width', 'height', 'length']}),
        ('Related parts', {'fields': ['related_parts']}),
    ]
    list_display = ('part_num', 'name', 'category', 'width', 'height', 'length',
                    'id', 'related_part_count')
    list_filter = ['width', 'height', 'length']
    search_fields = ['part_num', 'name', 'category__name']
    readonly_fields = ['related_parts']

    def related_parts(self, obj):  # pylint:disable=no-self-use
        return ', '.join(p.child_part.part_num for p in obj.get_related_parts(
            parents=True, children=True, transitive=True))

    def related_part_count(self, obj):  # pylint:disable=no-self-use
        return F'{obj.related_part_count()}'


class PartExternalIdpAdmin(admin.ModelAdmin):
    list_display = ('part', 'provider', 'external_id')


class PartRelationshipAdmin(admin.ModelAdmin):
    list_display = ('parent_part', 'child_part')


class UserPartAdmin(admin.ModelAdmin):
    list_display = ('user', 'part')


class InventoryAdmin(admin.ModelAdmin):
    list_display = ('userpart', 'color', 'qty')


# Register your models here.
admin.site.register(Color, ColorAdmin)
admin.site.register(Part, PartAdmin)
admin.site.register(PartCategory)
admin.site.register(PartRelationship, PartRelationshipAdmin)
admin.site.register(PartExternalId, PartExternalIdpAdmin)
admin.site.register(UserPart, UserPartAdmin)
admin.site.register(Inventory, InventoryAdmin)
