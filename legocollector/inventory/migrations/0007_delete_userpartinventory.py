# Generated by Django 2.2.4 on 2019-09-09 09:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0006_auto_20190909_1911'),
    ]

    operations = [
        migrations.DeleteModel(
            name='UserPartInventory',
        ),
    ]