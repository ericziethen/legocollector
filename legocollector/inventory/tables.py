
from django.contrib.staticfiles import finders
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.utils.html import format_html
from django_tables2 import CheckBoxColumn, Column, LinkColumn, Table
from django_tables2.utils import Accessor
from django_tables2.views import SingleTableMixin  # (for import in views.py)  pylint: disable=unused-import

from .models import Part, UserPart


class PartImage(Column):
    def render(self, value):
        rel_pic_path = F'inventory/PartColours/parts_-1/{value}.png'
        pic_url = static(rel_pic_path)
        abs_pic_path = finders.find(rel_pic_path)

        if abs_pic_path:
            img_class = 'part_image_zoom'
        else:
            img_class = 'image_not_found'

        return format_html(F'<img src="{pic_url}" alt="Part Picture" class="{img_class}" height="50" width="50">')


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
