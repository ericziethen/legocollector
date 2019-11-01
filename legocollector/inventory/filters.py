from django import template

from django_filters import CharFilter, FilterSet, ModelChoiceFilter
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
    part_num_contains = CharFilter(field_name='part__part_num', lookup_expr='icontains')
    category = ModelChoiceFilter(empty_label='### Category ###', field_name='part__category',
                                 queryset=PartCategory.objects.all())

    class Meta:
        model = UserPart
        fields = []
