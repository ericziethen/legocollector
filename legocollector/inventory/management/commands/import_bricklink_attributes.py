import logging

from defusedxml import ElementTree as ET

from django.db import transaction
from django.core.management.base import BaseCommand
from inventory.models import Part, PartExternalId

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('parts_xml_path', type=str)

    def handle(self, *args, **options):  # pylint: disable=too-many-locals,too-many-branches
        parts_xml_path = options['parts_xml_path']

        logger.info('Importing Part Attributes')
        # parse the xml file
        tree = ET.parse(parts_xml_path)
        root = tree.getroot()

        attributes_set_count = 0

        bricklink_external_ids = [
            e.external_id for e in PartExternalId.objects.filter(provider=PartExternalId.BRICKLINK)]

        with transaction.atomic():
            for idx, item_tag in enumerate(root.findall('ITEM')):  # pylint: disable=too-many-nested-blocks
                item_id = item_tag.find('ITEMID').text
                item_x = item_tag.find('ITEMDIMX').text
                item_y = item_tag.find('ITEMDIMY').text
                item_z = item_tag.find('ITEMDIMZ').text

                if item_id and any([item_x, item_y, item_z]):
                    part_list = []

                    # First check for Bricklink ID and part_nums as backup
                    if item_id in bricklink_external_ids:
                        # Allow for different bricklink IDs to point to the same part
                        part_list = [e.part for e in PartExternalId.objects.filter(
                            provider=PartExternalId.BRICKLINK, external_id=item_id)]
                    else:
                        part = Part.objects.filter(part_num=item_id).first()
                        if part:
                            part_list.append(part)

                    # Update related parts
                    for part in part_list:
                        if item_x and item_y and (item_y > item_x):
                            part.length = item_y
                            part.width = item_x
                        else:
                            part.length = item_x
                            part.width = item_y
                        part.height = item_z
                        part.save()

                        attributes_set_count += 1

                        if (attributes_set_count % 1000) == 0:
                            logger.info(F'   Attributes Set on: {attributes_set_count} parts')
                else:
                    logger.debug(F'  Invalid item Id Found: "{item_id}"')

                if (idx % 1000) == 0:
                    logger.info(F'  Items Processed: {idx}')

        logger.info(F'  Total Attributes Set on: {attributes_set_count} parts')
