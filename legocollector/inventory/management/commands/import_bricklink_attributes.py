
import csv
import os

from collections import OrderedDict

from xml.etree import ElementTree as ET

from django.db import transaction
from django.core.management.base import BaseCommand, CommandError
from inventory.models import Color, PartCategory, Part, PartRelationship


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('parts_xml_path', type=str)

    def handle(self, *args, **options):
        parts_xml_path = options['parts_xml_path']

        # Import Attributes
        updated_parts_dic = self._import_attributes(parts_xml_path)

        # Calculate Related Attributes
        self._calc_related_attributes(updated_parts_dic)

    def _import_attributes(self, parts_xml_path):
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
                item_name = item_tag.find('ITEMNAME').text

                if item_id:
                    if any([item_x, item_y, item_z]):
                        part = Part.objects.filter(part_num=item_id).first()


                        !!! TODO
                        When getting the part by name, multiple might have an identical name !!!
                        Need to handle all
                            -> Have separate function for each part

                        !!! TODO
                            - See if can get more relationships based on bricklink

                            e.g. bricklink:
                                    130	Baseplate, Road	6099px1	Baseplate, Road 32 x 32 9-Stud Landing Pad with Runway 'V' Pattern	100	32 x 32 x 0
                                rebrickable
                                    6099,Baseplate 32 x 32 Road 9-Stud Landing Pad,1,1
                                    6099p01,Baseplate 32 x 32 Road 9-Stud Landing Pad with Runway Print,1,1
                                    6099p02,Baseplate Road 32 x 32 9-Stud Landing Pad with Green Octagon Print [6988 / 6710],1,1
                                    6099p03,Baseplate Road 32 x 32 9-Stud Landing Pad with Yellow Circle Print,1,1
                                    6099p05,Baseplate 32 x 32 Road 9-Stud Landing Pad Type 2 (Orange),1,1
                                    6099p06,Baseplate 32 x 32 Road 9-Stud Landing Pad Type 3 (Orange),1,1


                        if not part:
                            part = Part.objects.filter(name=item_name).first()

                        if part:
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

    def _calc_related_attributes(self, updated_parts_dic):
        self.stdout.write(F'Calculating Related Part Attributes')
        related_updated_dic = updated_parts_dic.copy()
        # Only look based on the original updated dic
        related_attributes_set_count = 0
        with transaction.atomic():
            for idx, part in enumerate(updated_parts_dic.values()):
                #print('CHecking Part:', part.part_num)
                for related_part in part.get_related_parts():
                    if related_part.part_num not in related_updated_dic:
                        related_part.width = part.width
                        related_part.length = part.length
                        related_part.height = part.height
                        related_part.save()

                        related_updated_dic[related_part.part_num] = True
                        related_attributes_set_count += 1

                if (idx % 1000) == 0:
                    self.stdout.write(F'  Items Processed: {idx}')

        self.stdout.write(F'  Attributes Set on: {related_attributes_set_count} related parts')
