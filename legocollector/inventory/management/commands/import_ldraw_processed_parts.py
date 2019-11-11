import json
import os

from django.core.management.base import BaseCommand
from django.db import transaction

from inventory.models import Part, PartExternalId


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

        self.import_ldraw_data(json_dic)


    def import_ldraw_data(self, data_dic):
        self.stdout.write(F'Importing Ldraw Data')
        parts_processed_counts = 0
        part_list = Part.objects.values_list('part_num', flat=True)

        ldraw_external_ids = [
            e.external_id for e in PartExternalId.objects.filter(provider=PartExternalId.LDRAW)]

        parts_not_found_list = []

        with transaction.atomic():
            for part_num, part_dic in data_dic.items():  # pylint: disable=too-many-nested-blocks
                part_list = []
                if part_num in ldraw_external_ids:
                    part_list = [e.part for e in PartExternalId.objects.filter(
                        provider=PartExternalId.LDRAW, external_id=part_num)]
                else:
                    part = Part.objects.filter(part_num=part_num).first()
                    if part:
                        part_list.append(part)
                    else:
                        parts_not_found_list.append(part_num)

                for part in part_list:
                    part.stud_count = part_dic['stud_count']
                    part.save

                    parts_processed_counts += 1
                    if (parts_processed_counts % 1000) == 0:
                        self.stdout.write(F'  {parts_processed_counts} Parts Processed')

        self.stdout.write(F'Parts not Found:\n{sorted(parts_not_found_list)}')
        self.stdout.write(F'Total of {parts_processed_counts} DB Parts Processed')
