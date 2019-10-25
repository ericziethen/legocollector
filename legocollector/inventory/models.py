
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

    category = models.ForeignKey(PartCategory, on_delete=models.CASCADE, related_name='parts')

    def __str__(self):
        return F'{self.name} ({self.part_num})'

    @property
    def attribute_count(self):
        return [bool(self.width), bool(self.height), bool(self.length)].count(True)

    def get_children(self, recursive=True, children_processed=None):
        child_rels = PartRelationship.objects.filter(parent_part=self)
        children = []

        if not children_processed:
            children_processed = []

        for relationship in child_rels:
            child = relationship.child_part
            children.append(child)
            if recursive and (self.part_num not in children_processed):
                children += child.get_children(children_processed.append(self.part_num))

        return children

    def get_parents(self, recursive=True, parents_processed=None):
        parent_rels = PartRelationship.objects.filter(child_part=self)
        parents = []

        if not parents_processed:
            parents_processed = []

        for relationship in parent_rels:
            parent = relationship.parent_part
            parents.append(parent)
            if recursive and (self.part_num not in parents_processed):
                parents += parent.get_parents(parents_processed.append(self.part_num))

        return parents

    def get_related_parts_OLD(self):
        # Get the Children
        related_parts = self.get_children()

        # Add Parents and avoid Duplicates, e.g. if circular dependency
        for part in self.get_parents():
            if part not in related_parts:
                related_parts.append(part)

        return related_parts

    def get_related_parts(self, *, parents, children, transitive):
        related_parts = []

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
