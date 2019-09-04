from django.contrib import admin

from .models import Color
from .models import Part
from .models import PartCategory
from .models import UserPart


class ColorAdmin(admin.ModelAdmin):
    fields = ['name', 'transparent', 'rgb']


class PartAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Identification', {'fields': ['part_num', 'name']}),
        ('Dimensions', {'fields': ['width', 'height', 'length']}),
        ('Attributes', {'fields': ['stud_count', 'multi_height', 'uneven_dimensions']}),
    ]


# Register your models here.
admin.site.register(Color, ColorAdmin)
admin.site.register(Part, PartAdmin)
admin.site.register(PartCategory)
admin.site.register(UserPart)
