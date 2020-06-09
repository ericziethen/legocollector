import logging
import re

from decimal import Decimal

from django.db import transaction
from django.core.management.base import BaseCommand
from inventory.models import Part

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.guess_dimensions()

    def guess_dimensions(self):
        logger.info('Guess Dimensions')
        part_list = Part.objects.all()
        part_updates = 0
        with transaction.atomic():
            for part in part_list:
                if part.dimension_set_count == 0:
                    guessed_dims = self.guess_dimension_from_name(part.name)
                    if guessed_dims:
                        part.width = guessed_dims[0]
                        part.length = guessed_dims[1]
                        part.height = guessed_dims[2]
                        part.save()

                        part_updates += 1

                        if part_updates and (part_updates % 1000) == 0:
                            logger.info(F'  Parts Updated: {part_updates}')

        logger.info(F'Total Dimensions Updated: {part_updates}')

    @staticmethod
    def guess_dimension_from_name(name):
        dim_tup = None
        pattern_2 = '(?P<wh1>[0-9]{1,}) *?x *?(?P<wh2>[0-9]{1,})'
        pattern_3 = '(?P<wh1>[0-9]{1,}) *?x *?(?P<wh2>[0-9]{1,}) *?x *?(?P<height>[0-9]{1,})'

        width = length = height = None

        # Check if 2 Dimensions Found
        result = re.search(pattern_3, name)

        if result:
            height = Decimal(result.group('height'))
        else:

            # Check if 2 Dimensions Found
            result = re.search(pattern_2, name)

        if result:
            cand_w = Decimal(result.group('wh1'))
            cand_h = Decimal(result.group('wh2'))

            if cand_w > cand_h:
                length = cand_w
                width = cand_h
            else:
                length = cand_h
                width = cand_w

            dim_tup = (width, length, height)

        return dim_tup
