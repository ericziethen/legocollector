
import csv
import os

from collections import OrderedDict

from django.db import transaction
from django.core.management.base import BaseCommand, CommandError
from inventory.models import Color, PartCategory, Part


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

        try:
            self._validate_config_path(import_dir, import_files.keys())
        except ValueError as error:
            raise CommandError(F'Failed to validate config path: {error}')

        # Process import files
        for file_path, import_func in import_files.items():
            with open(file_path) as csvfile:
                reader = csv.DictReader(csvfile)
                import_func(reader)

    def _validate_config_path(self, base_path, expected_file_list):
        # Check path exists as directory
        if not os.path.exists(base_path) or not os.path.isdir(base_path):
            raise ValueError(F'{base_path} is not a valid DIrectory')

        # Check all expected files are present
        for file_path in expected_file_list:
            if not os.path.exists(file_path):
                raise ValueError(F'Expected file "{file_path}" not found')

    # TODO - All populate functions should use a generic approach
    def _populate_colors(self, csv_data):
        with transaction.atomic():
            for row in csv_data:
                Color.objects.get_or_create(
                    id=row['id'],
                    name=row['name'],
                    rgb=row['rgb'],
                    transparent=row['is_trans'])

    def _populate_part_categories(self, csv_data):
        with transaction.atomic():
            for row in csv_data:
                PartCategory.objects.get_or_create(
                    id=row['id'],
                    name=row['name'])

    def _populate_parts(self, csv_data):
        # TODO - This should be wrapped into a context manager so we can use it easier for multiple tables
        part_list = Part.objects.values_list('part_num', flat=True)
        with transaction.atomic():
            for row in csv_data:
                part_num = row['part_num']
                if part_num not in part_list:
                    Part.objects.create(
                        part_num=row['part_num'],
                        name=row['name'],
                        category_id=PartCategory.objects.get(id=row['part_cat_id']))
