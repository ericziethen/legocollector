import colorsys
import math

from django.db import models
from django.db.models import Sum
from django.contrib.auth.models import User
from django.urls import reverse


class PartCategory(models.Model):
    id = models.IntegerField(primary_key=True, editable=False)
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class Color(models.Model):
    id = models.IntegerField(primary_key=True, editable=False)
    name = models.CharField(max_length=200, unique=True)
    rgb = models.CharField(max_length=6)
    transparent = models.BooleanField(default=False)

    # These fields are only here to help with sorting the queryset nicely
    # can do the sorting in a lambda method, but some places expect a queryset
    color_step_hue = models.IntegerField(editable=False, default=0)
    color_step_lumination = models.DecimalField(
        max_digits=23, decimal_places=20, editable=False, default=0)
    color_step_value = models.IntegerField(editable=False, default=0)

    class Meta:
        ordering = ('transparent', 'color_step_hue', 'color_step_lumination', 'color_step_value')

    @property
    def rgb_ints(self):
        return (int(self.rgb[:2], 16), int(self.rgb[2:4], 16), int(self.rgb[4:], 16))

    @property
    def complimentary_color(self):
        # https://codepen.io/WebSeed/pen/pvgqEq
        color = 'FFFFFF'  # white
        if self.solor_is_light(self.rgb_ints[0], self.rgb_ints[1], self.rgb_ints[2]):
            color = '000000'  # black
        return color

    @staticmethod
    def solor_is_light(red, green, blue):  # https://codepen.io/WebSeed/pen/pvgqEq
        value = 1 - (0.299 * red + 0.587 * green + 0.114 * blue) / 255
        return value < 0.5

    @staticmethod
    def color_step(red, green, blue, repetitions=8):
        lum = math.sqrt(.241 * red + .691 * green + .068 * blue)

        hue, _, value = colorsys.rgb_to_hsv(red, green, blue)

        hue2 = int(hue * repetitions)
        value2 = int(value * repetitions)

        if hue2 % 2 == 1:
            value2 = repetitions - value2
            lum = repetitions - lum

        return (hue2, lum, value2)

    def save(self, *args, **kwargs):  # pylint: disable=arguments-differ
        hlv = self.color_step(self.rgb_ints[0], self.rgb_ints[1], self.rgb_ints[2])
        self.color_step_hue = hlv[0]
        self.color_step_lumination = hlv[1]
        self.color_step_value = hlv[2]
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Part(models.Model):
    part_num = models.CharField(unique=True, max_length=20)
    name = models.CharField(max_length=250)
    width = models.DecimalField(max_digits=8, decimal_places=4, blank=True, null=True)
    height = models.DecimalField(max_digits=8, decimal_places=4, blank=True, null=True)
    length = models.DecimalField(max_digits=8, decimal_places=4, blank=True, null=True)
    stud_count = models.PositiveIntegerField(blank=True, null=True)
    image_url = models.CharField(max_length=250, blank=True, null=True)

    category = models.ForeignKey(PartCategory, on_delete=models.CASCADE, related_name='parts')

    def save(self, *args, **kwargs):  # pylint: disable=arguments-differ
        if self.length is not None and self.width is not None:
            if self.width > self.length:
                temp_width = self.width
                self.width = self.length
                self.length = temp_width
        super().save(*args, **kwargs)

    def __str__(self):
        return F'{self.name} ({self.part_num})'

    @property
    def dimension_set_count(self):
        return [self.width is not None, self.height is not None, self.length is not None].count(True)

    @property
    def available_colors(self):
        return Color.objects.filter(setparts__part=self).distinct()

    @property
    def available_colors_count(self):
        return self.available_colors.count()

    @property
    def available_colors_str(self):
        return ', '.join(c.name for c in self.available_colors.order_by('name'))

    def get_related_parts(self, *, parents, children, transitive, parts_processed=None):
        related_parts = []

        if not parts_processed:
            parts_processed = []

        my_related_parts = []
        if parents:
            my_related_parts += [r.parent_part for r in PartRelationship.objects.filter(child_part=self)]
        if children:
            my_related_parts += [r.child_part for r in PartRelationship.objects.filter(parent_part=self)]

        if transitive:
            parts_processed.append(self.part_num)
            for part in my_related_parts:
                if part.part_num not in parts_processed:
                    related_parts.append(part)
                    related_parts += part.get_related_parts(
                        parents=parents, children=children, transitive=transitive,
                        parts_processed=parts_processed)
        else:
            related_parts = my_related_parts

        return related_parts

    def related_part_count(self, *, parents, children, transitive):
        return len(self.get_related_parts(parents=parents, children=children, transitive=transitive))


class PartRelationship(models.Model):
    child_part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name='parent')
    parent_part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name='child')

    # pylint: disable=invalid-name
    ALTERNATE_PART = 'Alternate part'
    DIFFERENT_MOLD = 'Different Mold'
    DIFFERENT_PRINT = 'Different Print'
    DIFFERENT_PATTERN = 'Different Pattern'
    # pylint: enable=invalid-name
    type_choices = [
        (ALTERNATE_PART, 'Part'),
        (DIFFERENT_MOLD, 'Mold'),
        (DIFFERENT_PRINT, 'Print'),
        (DIFFERENT_PATTERN, 'Pattern'),
    ]
    relationship_type = models.CharField(max_length=32, choices=type_choices)

    class Meta:
        unique_together = (('child_part', 'parent_part'),)

    def __str__(self):
        return F'{self.parent_part.part_num} => {self.relationship_type} => {self.child_part.part_num}'


class PartExternalId(models.Model):
    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name='external_ids')
    external_id = models.CharField(max_length=32)

    # pylint: disable=invalid-name
    BRICKLINK = 'BrickLink'
    BRICKOWL = 'BrickOwl'
    BRICKSET = 'Brickset'
    LDRAW = 'Ldraw'
    LEGO = 'Lego'
    PEERON = 'Peeron'
    # pylint: enable=invalid-name
    provider_list = [
        (BRICKLINK, 'BrickLink'),
        (BRICKOWL, 'BrickOwl'),
        (BRICKSET, 'Brickset'),
        (LDRAW, 'Ldraw'),
        (LEGO, 'Lego'),
        (PEERON, 'Peeron'),
    ]
    provider = models.CharField(max_length=32, choices=provider_list)

    class Meta:
        unique_together = (('part', 'provider', 'external_id'),)


class UserPart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_parts')
    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name='user_parts')

    class Meta:
        unique_together = (('user', 'part'),)

    @property
    def inventory_count(self):
        inv_count = Inventory.objects.filter(
            userpart__user=self.user, userpart=self).aggregate(Sum('qty'))
        # Query could return "{'qty__sum': None}"
        return inv_count['qty__sum'] or 0

    @property
    def used_colors(self):
        return Color.objects.filter(inventory_colors__userpart=self).distinct()

    @property
    def used_colors_str(self):
        return ', '.join(c.name for c in self.used_colors.order_by('name'))

    @property
    def unused_colors(self):
        return self.part.available_colors.exclude(pk__in=self.used_colors)

    def __str__(self):
        return F'{self.part.name} ({self.part.part_num})'

    def get_absolute_url(self):
        return reverse('userpart_detail', kwargs={'pk1': self.pk})


class Inventory(models.Model):
    userpart = models.ForeignKey(UserPart, on_delete=models.CASCADE, related_name='inventory_list')
    color = models.ForeignKey(Color, on_delete=models.CASCADE, related_name='inventory_colors')
    qty = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = (('userpart', 'color'),)

    def __str__(self):
        return F'{self.qty} x {self.color} ({self.userpart})'

    def get_absolute_url(self):
        return reverse('inventory_detail', kwargs={'pk1': self.pk, 'pk2': self.pk})


class SetPart(models.Model):

    # In the future that might need to be a foreign key if we ever introduce sets
    set_inventory = models.PositiveIntegerField()
    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name='setparts')
    color = models.ForeignKey(Color, on_delete=models.CASCADE, related_name='setparts')
    qty = models.PositiveIntegerField()
    is_spare = models.BooleanField()

    class Meta:
        unique_together = (('set_inventory', 'part', 'color', 'is_spare'),)

    def __str__(self):
        return F'{self.part} - {self.qty} x {self.color}'
