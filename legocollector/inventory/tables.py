from django_tables2 import CheckBoxColumn, LinkColumn, Table
from django_tables2.utils import Accessor
from django_tables2.views import SingleTableMixin

from .models import Part, UserPart

class PartTable(Table):
    box_selection = CheckBoxColumn(accessor='id')

    class Meta:  # pylint: disable=too-few-public-methods
        model = Part
        fields = ('part_num', 'name', 'width', 'height', 'length', 'stud_count', 'multi_height',
                  'uneven_dimensions', 'category_id')
        attrs = {"class": "table-striped table-bordered"}
        empty_text = "No Parts Found"


class UserPartTable(Table):
    part = LinkColumn(None, accessor='part.name', args=[Accessor('pk1')])

    class Meta:  # pylint: disable=too-few-public-methods
        model = UserPart
        fields = ['part', 'part.part_num', 'part.category_id', 'part.width', 'part.height', 'part.length',
                  'part.stud_count', 'part.multi_height', 'part.uneven_dimensions']
