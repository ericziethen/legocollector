# Generated by Django 2.2.5 on 2019-09-19 00:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0008_auto_20190919_0952'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userpart',
            name='part',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_parts', to='inventory.Part'),
        ),
    ]
