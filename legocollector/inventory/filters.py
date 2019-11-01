from django import template

from django_filters import FilterSet, ModelChoiceFilter
from django_filters.views import FilterView  # (for import in views.py)  pylint: disable=unused-import

from .models import UserPart, Part, PartCategory

register = template.Library()


@register.filter
def color_id_to_rgb(value):
    print(F'Filter:color_id_to_rgb: {value}')
    return value


class PartFilter(FilterSet):
    category = ModelChoiceFilter(empty_label='### Category ###', field_name='category',
                                 queryset=PartCategory.objects.all())

    class Meta:
        model = Part
        fields = {
            'width': ['exact', 'lt', 'gt', 'range'],
            'length': ['exact', 'lt', 'gt', 'range'],
            'height': ['exact', 'lt', 'gt', 'range'],
            'part_num': ['contains'],
            'name': ['contains'],
            'category': ['exact'],
        }


class UserPartFilter(FilterSet):

    class Meta:
        model = UserPart
        fields = {
            'part__width': ['exact', 'lt', 'gt', 'range'],
            'part__length': ['exact', 'lt', 'gt', 'range'],
            'part__height': ['exact', 'lt', 'gt', 'range'],
            'part__part_num': ['contains'],
            'part__name': ['contains'],
        }

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        super().__init__(data, queryset, request=request, prefix=prefix)
        self.filters['category'] = ModelChoiceFilter(
            empty_label='### Category ###', field_name='part__category',
            queryset=PartCategory.objects.filter(parts__user_parts__user=request.user).distinct().order_by('name'))
