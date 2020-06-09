import logging

from collections import defaultdict

from django.db import transaction
from django.core.management.base import BaseCommand
from inventory.models import Part

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


class Command(BaseCommand):

    def handle(self, *args, **options):  # pylint: disable=too-many-locals, too-many-branches, too-many-statements
        logger.info('Calculating Related Part Attributes')

        processed_parts = {}

        attribute_updates = defaultdict(int)

        with transaction.atomic():
            for idx, part in enumerate(Part.objects.all(), 1):
                if part.part_num not in processed_parts:
                    # Update Related Parts
                    part_list = self.set_related_attribs_for_part(
                        part, attribute_updates=attribute_updates)

                    # Remember Processed Parts
                    for rel_part in part_list:
                        processed_parts[rel_part.part_num] = True

                if (idx % 1000) == 0:
                    logger.info(F'  {idx} Parts Processed')

        self.print_update_details(attribute_updates)

    @staticmethod
    def print_update_details(attribute_updates):
        logger.info('  Attribute updates')
        logger.info(F'    Total Parts Updated: {attribute_updates["total_parts"]}')
        for group, count in attribute_updates.items():
            if group == 'total_parts':
                continue
            logger.info(F'    {group:<20}: Count: {count}')

    @staticmethod
    def set_related_attribs_for_part(part, *, attribute_updates):
        # For Processing Stud Counts we need to be carefull as related parts may have a different stud count
        # e.g. the following 2 related parts have a different stud count
        #       https://rebrickable.com/parts/10a/baseplate-24-x-32-with-squared-corners/
        #       https://rebrickable.com/parts/10b/baseplate-24-x-32-with-rounded-corners/

        # Get list of Related Parts
        related_parts = part.get_related_parts(parents=True, children=True, transitive=True)
        part_family = sorted(related_parts + [part], key=lambda p: p.dimension_set_count, reverse=True)

        rel_attrib_fields = ['width', 'height', 'length', 'top_studs', 'bottom_studs', 'stud_rings', 'image_url']

        # Get master Dimension to set
        master_part = part_family[0]
        master_attribs = {name: getattr(master_part, name)
                          for name in rel_attrib_fields if getattr(master_part, name) is not None}

        # Fill the rest with non clashing attribs
        for field in rel_attrib_fields:
            if field not in master_attribs:
                for rel_part in part_family:
                    val = getattr(rel_part, field)
                    if val is not None:
                        master_attribs[field] = val
                        break

        # Set the default Attribs
        for rel_part in part_family:
            part_update = False
            for field, value in master_attribs.items():
                if getattr(rel_part, field) is None:
                    setattr(rel_part, field, value)
                    attribute_updates[field] += 1
                    part_update = True

            if part_update:
                rel_part.save()
                attribute_updates['total_parts'] += 1

                if (attribute_updates['total_parts'] % 1000) == 0:
                    logger.info(F'''  Attributes Updated: {attribute_updates['total_parts']}''')

        return part_family
