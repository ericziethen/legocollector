from django.db import transaction
from django.core.management.base import BaseCommand
from inventory.models import Part


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write(F'Calculating Related Part Attributes')

        processed_parts = {}

        # Build the ordered part list
        part_list = sorted(Part.objects.all(), key=lambda p: p.attribute_count, reverse=True)

        self.print_attribute_details()

        related_attributes_set_count = 0
        with transaction.atomic():
            for part in part_list:
                if part.attribute_count > 0:
                    for related_part in part.get_related_parts():
                        if (related_part.part_num not in processed_parts) and\
                                (part.attribute_count > related_part.attribute_count):
                            related_part.width = part.width
                            related_part.length = part.length
                            related_part.height = part.height
                            related_part.save()

                            processed_parts[related_part.part_num] = True
                            related_attributes_set_count += 1

                if related_attributes_set_count and (related_attributes_set_count % 1000) == 0:
                    self.stdout.write(F'  Attributes Set: {related_attributes_set_count}')

        self.stdout.write(F'  Attributes Set on: {related_attributes_set_count} related parts')
        self.print_attribute_details()

    def print_attribute_details(self):
        self.stdout.write(F'Parts without Width:  {Part.objects.filter(width__isnull=True).count()}')
        self.stdout.write(F'Parts without Length: {Part.objects.filter(length__isnull=True).count()}')
        self.stdout.write(F'Parts without Height: {Part.objects.filter(height__isnull=True).count()}')
        part_list = Part.objects.filter(width__isnull=True, length__isnull=True, height__isnull=True)
        self.stdout.write(F'Parts without any:    {part_list.count()}')
