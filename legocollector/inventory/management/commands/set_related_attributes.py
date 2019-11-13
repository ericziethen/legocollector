from django.db import transaction
from django.core.management.base import BaseCommand
from inventory.models import Part


class Command(BaseCommand):

    def handle(self, *args, **options):
        self.stdout.write(F'Calculating Related Part Attributes')

        processed_parts = {}

        # Build the ordered part list
        self.print_attribute_details()

        related_attributes_set_count = 0
        related_stud_counts_set = 0
        with transaction.atomic():
            for idx, part in enumerate(Part.objects.all()):
                if part.part_num not in processed_parts:
                    related_parts = part.get_related_parts(parents=True, children=True, transitive=True)

                    part_family = sorted(related_parts + [part], key=lambda p: p.attribute_count, reverse=True)

                    # For Processing Stud Counts we need to be carefull as related parts may have a different stud count
                    # e.g. the following 2 related parts have a different stud count
                    #       https://rebrickable.com/parts/10a/baseplate-24-x-32-with-squared-corners/
                    #       https://rebrickable.com/parts/10b/baseplate-24-x-32-with-rounded-corners/

                    # Figure out the Stud Count, only take the count if there are not more than 1 different stud counts
                    stud_count = None
                    for related_part in part_family:
                        if related_part.stud_count is not None:
                            if stud_count and stud_count != related_part.stud_count:
                                # a different stud count found, igore whole family
                                stud_count = None
                                break

                            if stud_count is None:
                                stud_count = related_part.stud_count

                    highest_count_part = part_family[0]  # Will always exist since we added ourselves
                    for related_part in part_family:
                        update = False

                        # Set the Attributes
                        if ((highest_count_part is not related_part) and
                                (highest_count_part.attribute_count > related_part.attribute_count)):
                            update = True
                            related_part.width = highest_count_part.width
                            related_part.length = highest_count_part.length
                            related_part.height = highest_count_part.height
                            related_attributes_set_count += 1

                        # Set the Stud Count
                        if stud_count is not None:
                            update = True
                            related_part.stud_count = stud_count
                            related_stud_counts_set += 1

                        if update:
                            related_part.save()

                        processed_parts[related_part.part_num] = True

                        if related_attributes_set_count and (related_attributes_set_count % 1000) == 0:
                            self.stdout.write(F'  Attributes Set: {related_attributes_set_count}')

                if (idx % 1000) == 0:
                    self.stdout.write(F'  {idx} Parts Processed')

        self.stdout.write(F'  Attributes Set on: {related_attributes_set_count} related parts')
        self.stdout.write(F'  Stud Count set on: {related_stud_counts_set} related parts')        
        self.print_attribute_details()

    def print_attribute_details(self):
        self.stdout.write(F'Parts without Width:  {Part.objects.filter(width__isnull=True).count()}')
        self.stdout.write(F'Parts without Length: {Part.objects.filter(length__isnull=True).count()}')
        self.stdout.write(F'Parts without Height: {Part.objects.filter(height__isnull=True).count()}')
        part_list = Part.objects.filter(width__isnull=True, length__isnull=True, height__isnull=True)
        self.stdout.write(F'Parts without any:    {part_list.count()}')
