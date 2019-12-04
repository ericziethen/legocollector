import logging

from collections import defaultdict

from django.core.management.base import BaseCommand

from inventory.models import Part, PartCategory

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


class Command(BaseCommand):

    def handle(self, *args, **options):  # pylint: disable=too-many-locals, too-many-branches, too-many-statements
        logger.info(F'Show Database Details')

        self.show_category_details()
        self.show_part_details()

    @staticmethod
    def show_part_details():
        logger.info('### PARTS ###')
        check_not_none_fields = {
            'Has Width': 'width',
            'Has Height': 'height',
            'Has Length': 'length',
            'Has Top Studs': 'top_studs',
            'Has Bottom Studs': 'bottom_studs',
            'Has Stud Rings': 'stud_rings',
            'Has Image URL': 'image_url',
        }
        parts_detail = {val: 0 for val in check_not_none_fields}

        part_count = 0
        dimension_set_count = defaultdict(int)

        # Collect part Data
        for part in Part.objects.all().iterator():

            part_count += 1
            dimension_set_count[part.dimension_set_count] += 1
            for name, attrib_name in check_not_none_fields.items():
                if getattr(part, attrib_name) is not None:
                    parts_detail[name] += 1

        # Print the Details
        logger.info(F'Part Count: {part_count}')

        # Display Part Details
        for name, count in parts_detail.items():
            logger.info(F'  {name:20}: True: {count:>7}, False: {part_count - count:>7}')

        # Display Attribute Set Counts
        logger.info(F'  Dimension Set Count')
        for dimension_count, part_count in sorted(dimension_set_count.items()):
            logger.info(F'    {dimension_count:<2}: {part_count}')

    @staticmethod
    def show_category_details():
        logger.info('### CATEGORIES ###')
        
        for category in PartCategory.objects.all().iterator():
            logger.info(F'Part Count: {category.parts.all().count():<5} x {category.name}')
