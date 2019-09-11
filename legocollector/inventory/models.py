
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
    part_num = models.CharField(primary_key=True, max_length=20)
    name = models.CharField(max_length=250)
    width = models.PositiveIntegerField(blank=True, null=True)
    height = models.PositiveIntegerField(blank=True, null=True)
    length = models.PositiveIntegerField(blank=True, null=True)
    stud_count = models.PositiveIntegerField(blank=True, null=True)
    multi_height = models.BooleanField(blank=True, null=True)
    uneven_dimensions = models.BooleanField(blank=True, null=True)

    category_id = models.ForeignKey(PartCategory, on_delete=models.CASCADE, related_name='parts')

    def __str__(self):
        return self.name


class UserPart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_parts')
    part = models.ForeignKey(Part, on_delete=models.CASCADE, db_column='part_num_id', related_name='user_parts')

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
        return reverse('inventory_detail', kwargs={'pk1': self.userpart_id, 'pk2': self.pk})
