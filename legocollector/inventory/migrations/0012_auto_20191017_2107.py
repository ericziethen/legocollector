# Generated by Django 2.2.5 on 2019-10-17 10:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0011_auto_20191017_2046'),
    ]

    operations = [
        migrations.RenameField(
            model_name='partrelationship',
            old_name='child_partt',
            new_name='child_part',
        ),
    ]
