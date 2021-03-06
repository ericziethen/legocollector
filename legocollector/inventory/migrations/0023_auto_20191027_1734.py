# Generated by Django 2.2.6 on 2019-10-27 06:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0022_auto_20191027_1502'),
    ]

    operations = [
        migrations.AlterField(
            model_name='setpart',
            name='color',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='setparts', to='inventory.Color'),
        ),
        migrations.AlterField(
            model_name='setpart',
            name='part',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='setparts', to='inventory.Part'),
        ),
    ]
