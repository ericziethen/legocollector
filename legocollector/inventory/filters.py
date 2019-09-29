from django_filters import CharFilter, FilterSet
from django_filters.views import FilterView  # (for import in views.py)  pylint: disable=unused-import

from .models import Part


class PartFilter(FilterSet):
    part_num_contains = CharFilter(field_name='part_num', lookup_expr='icontains')

    class Meta:
        model = Part
        fields = ('part_num', 'name', 'width', 'height', 'length', 'stud_count', 'multi_height',
                  'uneven_dimensions', 'category_id')
