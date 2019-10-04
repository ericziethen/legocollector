from django.contrib.staticfiles.templatetags.staticfiles import static
from django.utils.html import format_html
from django_tables2 import CheckBoxColumn, Column, LinkColumn, Table
from django_tables2.utils import Accessor
from django_tables2.views import SingleTableMixin  # (for import in views.py)  pylint: disable=unused-import

from .models import Part, UserPart


class PartImage(Column):
    def render(self, value):
        pic_url = static(F'inventory/PartColours/parts_-1/{value}.png')
        return format_html(F'<img src="{pic_url}" alt="Part Picture" height="50" width="50">')


class PartTable(Table):
    box_selection = CheckBoxColumn(accessor='id')
    image = PartImage(accessor='part_num', verbose_name='Image')

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
