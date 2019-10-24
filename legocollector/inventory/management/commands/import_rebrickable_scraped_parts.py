import json
import os

from django.core.management.base import BaseCommand
from django.db import transaction

from inventory.models import Part, PartExternalId


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
            self.stderr.write(F'ERROR - Json file "{json_file_path}" does not exist')

        self.import_external_ids(json_dic['parts'])

    def import_external_ids(self, part_dic):
        self.stdout.write(F'Importing External IDs')
        external_id_counts = 0
        with transaction.atomic():
            for part_num, external_ids in part_dic.items():
                part = Part.objects.filter(part_num=part_num).first()
                if part:
                    for name, ids in external_ids['external_ids'].items():
                        provider = self.provider_from_string(name)
                        for entry in ids:
                            # Is this better than check if exist first?
                            PartExternalId.objects.get_or_create(
                                part=part,
                                external_id=entry.strip(),
                                provider=provider
                            )
                            # TODO - ARE WE MISSING A SAVE HERE ???
                            external_id_counts += 1

                            if (external_id_counts % 1000) == 0:
                                self.stdout.write(F'  {external_id_counts} External IDs imported')

        self.stdout.write(F'Total of {external_id_counts} External IDs imported')

    def provider_from_string(self, text):  # pylint: disable=no-self-use
        return TEXT_TO_PROVIDER_DIC[text]
