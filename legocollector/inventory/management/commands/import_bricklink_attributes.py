from defusedxml import ElementTree as ET

from django.db import transaction
from django.core.management.base import BaseCommand
from inventory.models import Part, PartExternalId


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('parts_xml_path', type=str)

    def handle(self, *args, **options):
        parts_xml_path = options['parts_xml_path']

        self.stdout.write(F'Importing Part Attributes')
        # parse the xml file
        tree = ET.parse(parts_xml_path)
        root = tree.getroot()

        attributes_set_count = 0
        updated_parts_dic = {}

        with transaction.atomic():
            for idx, item_tag in enumerate(root.findall('ITEM')):
                item_id = item_tag.find('ITEMID').text
                item_x = item_tag.find('ITEMDIMX').text
                item_y = item_tag.find('ITEMDIMY').text
                item_z = item_tag.find('ITEMDIMZ').text

                if item_id:
                    if any([item_x, item_y, item_z]):
                        part_list = []
                        part_external_ids = PartExternalId.objects.filter(
                            provider=PartExternalId.BRICKLINK,
                            external_id=item_id
                        )
                        if part_external_ids:
                            part_list = [p.part for p in part_external_ids]
                        else:
                            part = Part.objects.filter(part_num=item_id).first()
                            if part:
                                part_list.append(part)

                        for part in part_list:
                            if item_x and item_y and (item_y > item_x):
                                part.length = item_y
                                part.width = item_x
                            else:
                                part.length = item_x
                                part.width = item_y
                            part.height = item_z
                            part.save()

                            updated_parts_dic[part.part_num] = part
                            attributes_set_count += 1

                            if (attributes_set_count % 1000) == 0:
                                self.stdout.write(F'   Attributes Set on: {attributes_set_count} parts')
                else:
                    self.stdout.write(F'  Invalid item Id Found: "{item_id}"')

                if (idx % 1000) == 0:
                    self.stdout.write(F'  Items Processed: {idx}')

        self.stdout.write(F'  Total Attributes Set on: {attributes_set_count} parts')

        return updated_parts_dic
