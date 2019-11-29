import logging

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
        conflicting_top_studss = {}
        related_image_urls_set = 0

        with transaction.atomic():
            for idx, part in enumerate(Part.objects.all(), 1):
                if part.part_num not in processed_parts:
                    related_parts = part.get_related_parts(parents=True, children=True, transitive=True)

                    part_family = sorted(related_parts + [part], key=lambda p: p.dimension_set_count, reverse=True)

                    # For Processing Stud Counts we need to be carefull as related parts may have a different stud count
                    # e.g. the following 2 related parts have a different stud count
                    #       https://rebrickable.com/parts/10a/baseplate-24-x-32-with-squared-corners/
                    #       https://rebrickable.com/parts/10b/baseplate-24-x-32-with-rounded-corners/

                    top_studs = None
                    image_url = None
                    for related_part in part_family:
                        # Figure out the Stud Count, only take the count if there are not more
                        # than 1 different stud counts
                        if related_part.top_studs is not None:
                            if top_studs and top_studs != related_part.top_studs:
                                # a different stud count found, igore whole family
                                top_studs = None
                                conflicting_top_studss[part.part_num] =\
                                    [(p.part_num, p.top_studs) for p in sorted(part_family, key=lambda p: p.part_num)]
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

                    highest_count_part = part_family[0]  # Will always exist since we added ourselves
                    for related_part in part_family:
                        update = False

                        # Set the Attributes
                        if ((highest_count_part is not related_part) and
                                (highest_count_part.dimension_set_count > related_part.dimension_set_count)):
                            update = True
                            related_part.width = highest_count_part.width
                            related_part.length = highest_count_part.length
                            related_part.height = highest_count_part.height
                            related_attributes_set_count += 1

                        # Set the Stud Count
                        if top_studs and related_part.top_studs is None:
                            update = True
                            related_part.top_studs = top_studs
                            related_top_studss_set += 1

                        # Set Image URL
                        if image_url and related_part.image_url is None:
                            update = True
                            related_part.image_url = image_url
                            related_image_urls_set += 1

                        if update:
                            related_part.save()

                        processed_parts[related_part.part_num] = True

                        if related_attributes_set_count and (related_attributes_set_count % 1000) == 0:
                            logger.info(F'  Attributes Set: {related_attributes_set_count}')

                if (idx % 1000) == 0:
                    logger.info(F'  {idx} Parts Processed')

        conflict_stud_str = '\n    '.join([F'%s:: %s' % (key, val) for (key, val) in conflicting_top_studss.items()])
        logger.info(F'  Conflicting StudCounts Families: \n    {conflict_stud_str}')
        logger.info(F'  Attributes Set on: {related_attributes_set_count} related parts')
        logger.info(F'  Stud Count set on: {related_top_studss_set} related parts.')
        logger.info(F'  Image Url set on:  {related_image_urls_set} related parts')
