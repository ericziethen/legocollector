# Generated by Django 2.2.6 on 2019-10-29 10:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0025_auto_20191028_1039'),
    ]

    operations = [
        migrations.AlterField(
            model_name='color',
            name='transparent',
            field=models.BooleanField(default=False),
        ),
    ]
