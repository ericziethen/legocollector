# Generated by Django 2.2.4 on 2019-09-05 22:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userpart',
            name='qty',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
