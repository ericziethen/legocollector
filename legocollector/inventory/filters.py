from django_filters import FilterSet, ModelChoiceFilter, CharFilter
from django_filters.views import FilterView  # (for import in views.py)  pylint: disable=unused-import

from .models import UserPart, Part, PartCategory
from django.forms.widgets import TextInput

class PartFilter(FilterSet):
    category = ModelChoiceFilter(empty_label='### Category ###', field_name='category',
                                 queryset=PartCategory.objects.all())
    test_filter = CharFilter(widget=TextInput(attrs={'title': 'test_filter'}))


    class Meta:
        model = Part
        fields = {
            'test_filter': ['exact'],
            'part_num': ['contains'],
            'width': ['exact', 'lt', 'gt', 'range'],
            'name': ['contains'],
            'length': ['exact', 'lt', 'gt', 'range'],
            'height': ['exact', 'lt', 'gt', 'range'],
            'top_studs': ['exact', 'lt', 'gt', 'range'],
            'bottom_studs': ['exact', 'lt', 'gt', 'range'],
            'stud_rings': ['exact', 'lt', 'gt', 'range'],
            'category': ['exact'],
        }

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):

        # Modifying extras, maybe the title ???
        # https://django-filter.readthedocs.io/en/master/ref/filters.html#filters

        # DISPLAY Title over hovering
        # https://stackoverflow.com/questions/27248121/text-display-on-mouse-over-field

        super().__init__(data, queryset, request=request, prefix=prefix)
        print('\nself.filters', self.filters)
        print('\nCATEGORY', self.filters['test_filter'].__dict__)
        print('\nbottom_studs', self.filters['bottom_studs'].__dict__)
        print('\nstud_rings__range', type(self.filters['stud_rings__range']),  self.filters['stud_rings__range'].__dict__)
        
        print('\nself.filters', type(self.filters))
        for name, my_filter in self.filters.items():
            print('my_filter', name, type(my_filter), my_filter, my_filter.extra)
            if type(my_filter) == dict:
                field_name = F'{my_filter["field_name"]}_{my_filter["lookup_expr"]}'
            else:
                print('No Fieldname for', name)

            #if 'extra'





class UserPartFilter(FilterSet):

    class Meta:
        model = UserPart
        fields = {
            'part__part_num': ['contains'],
            'part__width': ['exact', 'lt', 'gt', 'range'],
            'part__name': ['contains'],
            'part__length': ['exact', 'lt', 'gt', 'range'],
            'part__height': ['exact', 'lt', 'gt', 'range'],
            'part__top_studs': ['exact', 'lt', 'gt', 'range'],
            'part__bottom_studs': ['exact', 'lt', 'gt', 'range'],
            'part__stud_rings': ['exact', 'lt', 'gt', 'range'],
        }

    def __init__(self, data=None, queryset=None, *, request=None, prefix=None):
        super().__init__(data, queryset, request=request, prefix=prefix)
        self.filters['category'] = ModelChoiceFilter(
            empty_label='### Category ###', field_name='part__category',
            queryset=PartCategory.objects.filter(parts__user_parts__user=request.user).distinct())
