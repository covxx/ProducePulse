# Generated by Django 4.2.13 on 2024-07-05 03:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0009_builder_alter_inventoryitem_built_by'),
    ]

    operations = [
        migrations.AlterField(
            model_name='inventoryitem',
            name='built_by',
            field=models.CharField(default='Enter Builder Name...', max_length=200),
        ),
        migrations.DeleteModel(
            name='Builder',
        ),
    ]
