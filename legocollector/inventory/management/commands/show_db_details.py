import logging

from collections import defaultdict

from django.core.management.base import BaseCommand

from inventory.models import Part

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


class Command(BaseCommand):

    def handle(self, *args, **options):  # pylint: disable=too-many-locals, too-many-branches, too-many-statements
        logger.info(F'Show Database Details')

        self.show_part_detaile()

    @staticmethod
    def show_part_detaile():
        check_not_none_fields = {
            'Has Width': 'width',
            'Has Height': 'height',
            'Has Length': 'length',
            'Has Stud Count': 'stud_count',
            'Has Image URL': 'image_url',
        }
        parts_detail = {val: 0 for val in check_not_none_fields}

        part_count = 0
        dimension_set_count = defaultdict(int)

        # Collect part Data
        for part in Part.objects.all().iterator():

            if part_count < 1:
                print(part.width, type(part.width))

            part_count += 1
            dimension_set_count[part.dimension_set_count] += 1
            for name, attrib_name in check_not_none_fields.items():
                if getattr(part, attrib_name) is not None:
                    parts_detail[name] += 1

        # Print the Details
        logger.info(F'Part Count: {part_count}')

        # Display Part Details
        for name, count in parts_detail.items():
            logger.info(F'  {name:<15}: True: {count:>7}, False: {part_count - count:>7}')

        # Display Attribute Set Counts
        logger.info(F'  Dimension Set Count')
        for dimension_count, part_count in sorted(dimension_set_count.items()):
            logger.info(F'    {dimension_count:<2}: {part_count}')
