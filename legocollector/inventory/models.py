
from django.db import models
from django.contrib.auth.models import User
# Create your models here.


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
    part_num = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=250)
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    length = models.PositiveIntegerField()
    stud_count = models.PositiveIntegerField()
    multi_height = models.BooleanField()
    uneven_dimensions = models.BooleanField()

    category_id = models.ForeignKey(PartCategory, on_delete=models.CASCADE)


class UserPart(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    part_id = models.ForeignKey(Part, on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('user_id', 'part_id', 'color'),)