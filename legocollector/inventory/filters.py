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
    part_num_contains = CharFilter(field_name='part_num', lookup_expr='icontains')
    category = ModelChoiceFilter(empty_label='### Category ###', field_name='category_id',
                                 queryset=PartCategory.objects.all())

    class Meta:
        model = Part
        fields = ('part_num', 'name', 'width', 'height', 'length', 'stud_count', 'multi_height',
                  'uneven_dimensions', 'category')


class UserPartFilter(FilterSet):
    part_num_contains = CharFilter(field_name='part__part_num', lookup_expr='icontains')
    category = ModelChoiceFilter(empty_label='### Category ###', field_name='part__category_id',
                                 queryset=PartCategory.objects.all())

    class Meta:
        model = UserPart
        fields = []
