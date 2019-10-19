
from django.db import models
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
    transparent = models.BooleanField()

    def __str__(self):
        return self.name


class Part(models.Model):
    part_num = models.CharField(unique=True, max_length=20)
    name = models.CharField(max_length=250)
    width = models.DecimalField(max_digits=8, decimal_places=4, blank=True, null=True)
    height = models.DecimalField(max_digits=8, decimal_places=4, blank=True, null=True)
    length = models.DecimalField(max_digits=8, decimal_places=4, blank=True, null=True)

    category_id = models.ForeignKey(PartCategory, on_delete=models.CASCADE, related_name='parts')

    def __str__(self):
        return F'{self.name} ({self.part_num})'

    def get_children(self):
        return [p.child_part for p in PartRelationship.objects.filter(parent_part=self)]

    def get_parents(self):
        return [p.parent_part for p in PartRelationship.objects.filter(child_part=self)]

    def get_related_parts(self):
        return self.get_children() + self.get_parents()

    def related_part_count(self):
        return len(self.get_related_parts())


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

    def __str__(self):
        return F'{self.parent_part.part_num} => {self.relationship_type} => {self.child_part.part_num}'


class UserPart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_parts')
    part = models.ForeignKey(Part, on_delete=models.CASCADE, related_name='user_parts')

    class Meta:
        unique_together = (('user', 'part'),)

    def __str__(self):
        return F'{self.part.name} ({self.part.part_num})'

    def get_absolute_url(self):
        return reverse('userpart_detail', kwargs={'pk1': self.pk})


class Inventory(models.Model):
    userpart = models.ForeignKey(UserPart, on_delete=models.CASCADE, related_name='inventory_list')
    color = models.ForeignKey(Color, on_delete=models.CASCADE, related_name='user_parts')
    qty = models.PositiveIntegerField(default=0)

    class Meta:
        unique_together = (('userpart', 'color'),)

    def __str__(self):
        return F'{self.qty} x {self.color} ({self.userpart})'

    def get_absolute_url(self):
        return reverse('inventory_detail', kwargs={'pk1': self.pk, 'pk2': self.pk})
