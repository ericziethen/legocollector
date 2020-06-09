import json
import logging
import os

from django.core.management.base import BaseCommand
from django.db import transaction

from inventory.models import Part, PartExternalId

logger = logging.getLogger(__name__)  # pylint: disable=invalid-name


TEXT_TO_PROVIDER_DIC = {
    'BrickLink': PartExternalId.BRICKLINK,
    'BrickOwl': PartExternalId.BRICKOWL,
    'Brickset': PartExternalId.BRICKSET,
    'LDraw': PartExternalId.LDRAW,
    'LEGO': PartExternalId.LEGO,
    'Peeron': PartExternalId.PEERON
}


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('json_file_path', type=str)

    def handle(self, *args, **options):
        json_file_path = options['json_file_path']

        json_dic = {}
        if os.path.exists(json_file_path):
            with open(json_file_path, 'r', encoding='utf-8') as file_ptr:
                json_dic = json.load(file_ptr)
        else:
            logger.error(F'ERROR - Json file "{json_file_path}" does not exist')

        self.import_scraped_data(json_dic['parts'])

    def import_scraped_data(self, data_dic):
        logger.info('Importing Scraped Data')
        external_id_counts = 0
        parts_processed_counts = 0
        part_list = Part.objects.values_list('part_num', flat=True)

        with transaction.atomic():
            for part_num, part_dic in data_dic.items():  # pylint: disable=too-many-nested-blocks
                if part_num in part_list:
                    part = Part.objects.filter(part_num=part_num).first()
                    if part:

                        # Import image url
                        part_img_url = part_dic['part_img_url']
                        if part_img_url:
                            part.image_url = part_img_url
                            part.save()

                        # Import External IDs
                        for name, ids in part_dic['external_ids'].items():
                            provider = self.provider_from_string(name)
                            for entry in ids:
                                # Is this better than check if exist first?
                                PartExternalId.objects.update_or_create(
                                    part=part,
                                    external_id=entry.strip(),
                                    provider=provider
                                )
                                external_id_counts += 1

                                if (external_id_counts % 1000) == 0:
                                    logger.debug(F'    {external_id_counts} External IDs imported')

                        parts_processed_counts += 1
                        if (parts_processed_counts % 1000) == 0:
                            logger.info(F'  {parts_processed_counts} Parts Processed')

        logger.info(F'Total of {parts_processed_counts} DB Parts Processed')
        logger.info(F'Total of {external_id_counts} External IDs imported')

    @staticmethod
    def provider_from_string(text):
        return TEXT_TO_PROVIDER_DIC[text]
