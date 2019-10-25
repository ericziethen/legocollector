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

            # !!! TODO - Partlist gets outdated
            # if related part get's processed, the same part might still be in the part list but with old data
            # I could use an iterator of the queryset, but then I cant iterate in an ordered matter
            # Maybe allow the part to be updated as well from the related part?
            #     -> But then we probably shouldn't igore already processed parts because the number might be increasing by 1 each time
            '''
            for idx, part in enumerate(Part.objects.all().iterator()):
                for related_part in part.get_related_parts():
                    #print(F'    Related Part: {related_part.part_num} - ({related_part.attribute_count})')
                    if part.attribute_count > related_part.attribute_count:
                        related_part.width = part.width
                        related_part.length = part.length
                        related_part.height = part.height
                        related_part.save()
                        related_attributes_set_count += 1
                        #print(F'    Related Part Saved: {related_part.width} - {related_part.length} - {related_part.height} - ({related_part.attribute_count})')
                    elif part.attribute_count < related_part.attribute_count:
                        part.width = related_part.width
                        part.length = related_part.length
                        part.height = related_part.height
                        part.save()
                        #print(F'    Part Saved: {part.width} - {part.length} - {part.height} - ({part.attribute_count})')
                        related_attributes_set_count += 1

                if (idx % 1000) == 0:
                    self.stdout.write(F'  {idx} Parts Processed')

                if related_attributes_set_count and (related_attributes_set_count % 1000) == 0:
                    self.stdout.write(F'  Attributes Set: {related_attributes_set_count}')

            '''
        for each part
            if part not processed
                get all related parts (transitively, including remote related)
                add part to the list
                sort parts py attribute count
                get the first part (will have the highest count)
                for each part in list
                    if part attrib count > then other part attrib count
                        update other part
                    flag part as processed (even if not set, they cannot come from somewhere else anymore)

            for idx, part in enumerate(part_list):
                #print(F'  PART: {part.part_num} - ({part.attribute_count})')
                if part.attribute_count > 0:
                    for related_part in part.get_related_parts():
                        #print(F'    Related Part: {related_part.part_num} - ({related_part.attribute_count}) - Processed? {related_part.part_num in processed_parts}')
                        if (related_part.part_num not in processed_parts) and\
                                (part.attribute_count > related_part.attribute_count):
                            related_part.width = part.width
                            related_part.length = part.length
                            related_part.height = part.height
                            related_part.save()
                            #print(F'    Related Part Saved: {related_part.width} - {related_part.length} - {related_part.height} - ({related_part.attribute_count})')

                            processed_parts[related_part.part_num] = True
                            related_attributes_set_count += 1

                if (idx % 1000) == 0:
                    self.stdout.write(F'  {idx} Parts Processed')

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
