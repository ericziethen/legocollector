import logging

from collections import defaultdict

from django.db import transaction
from django.core.management.base import BaseCommand
from inventory.models import Part

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


class Command(BaseCommand):

    def handle(self, *args, **options):  # pylint: disable=too-many-locals, too-many-branches, too-many-statements
        logger.info(F'Calculating Related Part Attributes')

        processed_parts = {}

        related_attributes_set_count = 0
        related_top_studss_set = 0

        attribute_updates = defaultdict(int)

        conflicting_attribs = {}
        conflicting_attribs['dimensions'] = {}
        conflicting_attribs['top_studs'] = {}
        conflicting_attribs['botom_studs'] = {}
        conflicting_attribs['stud_rings'] = {}

        related_image_urls_set = 0

        with transaction.atomic():
            for idx, part in enumerate(Part.objects.all(), 1):
                if part.part_num not in processed_parts:

                    # Get list of Related Parts
                    related_parts = part.get_related_parts(parents=True, children=True, transitive=True)
                    part_family = sorted(related_parts + [part], key=lambda p: p.dimension_set_count, reverse=True)

                    # Update Related Parts
                    self.set_related_attribs_for_part_list(
                        part_family, attribute_updates=attribute_updates,
                        conflicting_attribs=conflicting_attribs)

                    # Remember Processed Parts
                    for rel_part in part_family:
                        processed_parts[rel_part.part_num] = True

                if (idx % 1000) == 0:
                    logger.info(F'  {idx} Parts Processed')

        logger.info(F'  Conflicting Attributes')
        for group, part_num_conflicts in conflicting_attribs.items():
            logger.info(F'    ### {group} ###')
            for part_num, conflict in part_num_conflicts.items():
                conflict_str = '\n      '.join([F'%s:: %s' % (key, val) for (key, val) in conflict.items()])
                logger.info(F'    Part: {part_num}: {conflict_str}')

        logger.info(F'  Attribute updates')
        for group, count in attribute_updates.items():
            logger.info(F'    {group:<20}: Count: {count}')

    @staticmethod
    def set_related_attribs_for_part_list(
            db_part_list, *, attribute_updates=None, conflicting_attribs=None):
        # For Processing Stud Counts we need to be carefull as related parts may have a different stud count
        # e.g. the following 2 related parts have a different stud count
        #       https://rebrickable.com/parts/10a/baseplate-24-x-32-with-squared-corners/
        #       https://rebrickable.com/parts/10b/baseplate-24-x-32-with-rounded-corners/

        top_studs = None
        image_url = None
        for related_part in db_part_list:
            # Figure out the Stud Count, only take the count if there are not more
            # than 1 different stud counts
            if related_part.top_studs is not None:
                if top_studs and top_studs != related_part.top_studs:
                    # a different stud count found, igore whole family
                    top_studs = None
                    if conflicting_attribs:
                        conflicting_attribs['top_studs'][related_part.part_num] =\
                            [(p.part_num, p.top_studs) for p in sorted(db_part_list, key=lambda p: p.part_num)]
                    break

                if top_studs is None:
                    top_studs = related_part.top_studs

            # Check the image url, only copy if none other set
            # It's quite likely that different part's have different urls, e.g. different prints
            # We could just guess it, but don't want to do that now
                if image_url and image_url != related_part.image_url:
                    # a different image_url found, igore whole family
                    image_url = None
                    break

                if image_url is None:
                    image_url = related_part.image_url

        highest_count_part = db_part_list[0]  # Will always exist since we added ourselves
        for related_part in db_part_list:
            update = False

            # Set the Attributes
            if ((highest_count_part is not related_part) and
                    (highest_count_part.dimension_set_count > related_part.dimension_set_count)):
                update = True
                related_part.width = highest_count_part.width
                related_part.length = highest_count_part.length
                related_part.height = highest_count_part.height
                if attribute_updates:
                    attribute_updates['dimensions'] += 1

            # Set the Stud Count
            if top_studs and related_part.top_studs is None:
                update = True
                related_part.top_studs = top_studs
                if attribute_updates:
                    attribute_updates['top_studs'] += 1

            # Set Image URL
            if image_url and related_part.image_url is None:
                update = True
                related_part.image_url = image_url
                if attribute_updates:
                    attribute_updates['image_url'] += 1

            if update:
                if attribute_updates:
                    attribute_updates['total_parts'] += 1
                related_part.save()

            if attribute_updates:
                if 'total_parts' in attribute_updates and (attribute_updates['total_parts'] % 1000) == 0:
                    logger.info(F'''  Attributes Set: {attribute_updates['total_parts']}''')
