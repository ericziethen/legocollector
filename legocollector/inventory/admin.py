from django.contrib import admin

from .models import Color
from .models import Part
from .models import PartCategory
from .models import UserPart

# Register your models here.
admin.site.register(Color)
admin.site.register(Part)
admin.site.register(PartCategory)
admin.site.register(UserPart)
