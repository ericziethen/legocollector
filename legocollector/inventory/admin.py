from django.contrib import admin

from .models import (
    Color, Part, PartCategory, PartRelationship,
    PartExternalId, SetPart, UserPart, Inventory
)


class ColorAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Basic', {'fields': ['name', 'transparent']}),
        ('Color', {'fields': ['rgb', 'complimentary_color']}),
        ('HLV', {'fields': ['color_step_hue', 'color_step_lumination', 'color_step_value']})
    ]
    readonly_fields = ['complimentary_color', 'color_step_hue', 'color_step_lumination', 'color_step_value', 'rgb_ints']
    list_display = ('name', 'transparent', 'rgb', 'complimentary_color', 'color_step_hue', 'color_step_lumination',
                    'color_step_value', 'rgb_ints')
    search_fields = ['name']


class PartAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Identification', {'fields': ['part_num', 'name', 'category', 'image_url']}),
        ('Dimensions', {'fields': ['width', 'height', 'length']}),
        ('Studs', {'fields': ['top_studs', 'bottom_studs', 'stud_rings']}),
        ('Available Colors', {'fields': ['available_colors']}),
        ('Set Inventories', {'fields': ['set_inventories']}),
        ('Related parts', {'fields': ['related_parts']}),
    ]
    list_display = ('part_num', 'name', 'category', 'width', 'height', 'length',
                    'top_studs', 'bottom_studs', 'stud_rings',
                    'id', 'related_part_count', 'set_count')
    list_filter = [
        'width', 'height', 'length',
        'top_studs', 'bottom_studs', 'stud_rings']
    search_fields = ['part_num', 'name', 'category__name']
    readonly_fields = ['related_parts', 'available_colors', 'set_inventories', 'set_count']

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
