from django.db import transaction
from django.core.management.base import BaseCommand
from inventory.models import Part


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write(F'Calculating Related Part Attributes')


        # !!! TODO !!!
        # I needed to run 2 passes to get all parts, why
        # Am I missing something in the order it sets related parts
        # Maybe
        # A is set, b and c not
        # A in first go, set b (after b had no attributes)
        # But it shouldn't be the case
        # Double check with attribute count


        processed_parts = {}

        self.print_attribute_details()

        related_attributes_set_count = 0
        with transaction.atomic():
            for count in [3, 2, 1]:
                parts = self.get_part_with_attributes_set(count)

                for part in parts:
                    if any([part.width, part.length, part.height]):
                        for related_part in part.get_related_parts():
                            if related_part.part_num not in processed_parts:
                                related_part.width = part.width
                                related_part.length = part.length
                                related_part.height = part.height
                                related_part.save()

                                processed_parts[related_part.part_num] = True
                                related_attributes_set_count += 1

                    if (related_attributes_set_count % 1000) == 0:
                        self.stdout.write(F'  Attributes Set: {related_attributes_set_count}')

        self.stdout.write(F'  Attributes Set on: {related_attributes_set_count} related parts')
        self.print_attribute_details()

    def get_part_with_attributes_set(self, count):
        return [part for part in Part.objects.all() if part.attribute_count == count]

    def print_attribute_details(self):
        self.stdout.write(F'Parts without Width:  {Part.objects.filter(width__isnull=True).count()}')
        self.stdout.write(F'Parts without Length: {Part.objects.filter(length__isnull=True).count()}')
        self.stdout.write(F'Parts without Height: {Part.objects.filter(height__isnull=True).count()}')
        part_list = Part.objects.filter(width__isnull=True, length__isnull=True, height__isnull=True)
        self.stdout.write(F'Parts without any:    {part_list.count()}')
