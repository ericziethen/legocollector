# Generated by Django 2.2.6 on 2019-10-27 23:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0024_auto_20191027_1755'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventory',
            name='color',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='inventory_colors', to='inventory.Color'),
        ),
    ]
