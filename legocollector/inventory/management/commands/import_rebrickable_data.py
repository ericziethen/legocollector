import colorsys
import csv
import math
import os

from collections import OrderedDict

from django.db import transaction
from django.core.management.base import BaseCommand, CommandError
from inventory.models import Color, PartCategory, Part, PartRelationship, SetPart


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('config_path', type=str)

    def handle(self, *args, **options):
        import_dir = options['config_path']

        # Supported files to import
        import_files = OrderedDict()
        import_files[os.path.join(import_dir, 'colors.csv')] = self._populate_colors
        import_files[os.path.join(import_dir, 'part_categories.csv')] = self._populate_part_categories
        import_files[os.path.join(import_dir, 'parts.csv')] = self._populate_parts
        import_files[os.path.join(import_dir, 'part_relationships.csv')] = self._populate_relationships
        import_files[os.path.join(import_dir, 'inventory_parts.csv')] = self._populate_set_parts

        try:
            self._validate_config_path(import_dir, import_files.keys())
        except ValueError as error:
            raise CommandError(F'Failed to validate config path: {error}')

        # Process import files
        for file_path, import_func in import_files.items():
            with open(file_path) as csvfile:
                reader = csv.DictReader(csvfile)
                import_func(reader)

    def _populate_colors(self, csv_data):
        self.stdout.write(F'Populate Colors')
        with transaction.atomic():
            for row in csv_data:
                rgb = row['rgb']
                color_step = self._color_step(
                    int(rgb[:2], 16), int(rgb[4:], 16), int(rgb[2:4], 16)
                )

                Color.objects.update_or_create(
                    id=row['id'],
                    defaults={
                        'rgb': rgb,
                        'name': row['name'],
                        'transparent': row['is_trans'],
                        'color_step_hue': color_step[0],
                        'color_step_lumination': color_step[1],
                        'color_step_value': color_step[2]
                    }
                )

    def _populate_part_categories(self, csv_data):
        self.stdout.write(F'Populate Part Categories')
        with transaction.atomic():
            for row in csv_data:
                PartCategory.objects.update_or_create(
                    id=row['id'],
                    defaults={'name': row['name']})

    def _populate_parts(self, csv_data):
        self.stdout.write(F'Populate Parts')
        part_list = Part.objects.values_list('part_num', flat=True)
        create_count = 0
        with transaction.atomic():
            for row in csv_data:
                part_num = row['part_num']
                if part_num not in part_list:
                    Part.objects.create(
                        part_num=row['part_num'],
                        name=row['name'],
                        category=PartCategory.objects.get(id=row['part_cat_id']))
                    create_count += 1

                    if (create_count % 1000) == 0:
                        self.stdout.write(F'  Parts Created {create_count}')
        self.stdout.write(F'  Total Parts Created {create_count}')

    def _populate_relationships(self, csv_data):
        self.stdout.write(F'Populate Relationships')
        with transaction.atomic():
            relation_mapping = {
                'A': PartRelationship.ALTERNATE_PART,
                'M': PartRelationship.DIFFERENT_MOLD,
                'P': PartRelationship.DIFFERENT_PRINT,
                'T': PartRelationship.DIFFERENT_PATTERN
            }

            part_list = Part.objects.values_list('part_num', flat=True)

            for idx, row in enumerate(csv_data, 1):
                rel_type = row['rel_type']
                child_part_num = row['child_part_num']
                parent_part_num = row['parent_part_num']

                if (child_part_num in part_list) and (parent_part_num in part_list):
                    child_part = Part.objects.filter(part_num=child_part_num).first()
                    parent_part = Part.objects.filter(part_num=parent_part_num).first()

                    if child_part and parent_part:
                        PartRelationship.objects.update_or_create(
                            child_part=child_part,
                            parent_part=parent_part,
                            defaults={'relationship_type': relation_mapping[rel_type]}
                        )

                        if (idx % 1000) == 0:
                            self.stdout.write(F'  Relationships Processed: {idx}')

    def _populate_set_parts(self, csv_data):
        self.stdout.write(F'Populate Set Parts')
        with transaction.atomic():
            for row in csv_data:
                SetPart.objects.update_or_create(
                    set_inventory=row['inventory_id'],
                    part=Part.objects.get(part_num=row['part_num']),
                    color=Color.objects.get(id=row['color_id']),
                    defaults={
                        'qty': row['quantity'],
                        'is_spare': row['is_spare']
                    }
                )

    @staticmethod
    def _validate_config_path(base_path, expected_file_list):
        # Check path exists as directory
        if not os.path.exists(base_path) or not os.path.isdir(base_path):
            raise ValueError(F'{base_path} is not a valid DIrectory')

        # Check all expected files are present
        for file_path in expected_file_list:
            if not os.path.exists(file_path):
                raise ValueError(F'Expected file "{file_path}" not found')

    @staticmethod
    def _color_step(red, green, blue, repetitions=8):
        lum = math.sqrt(.241 * red + .691 * green + .068 * blue)

        hue, _, value = colorsys.rgb_to_hsv(red, green, blue)

        hue2 = int(hue * repetitions)
        value2 = int(value * repetitions)

        if hue2 % 2 == 1:
            value2 = repetitions - value2
            lum = repetitions - lum

        return (hue2, lum, value2)
