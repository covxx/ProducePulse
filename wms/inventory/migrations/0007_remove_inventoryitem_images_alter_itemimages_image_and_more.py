# Generated by Django 4.2.13 on 2024-07-04 04:28

from django.db import migrations, models
import django.db.models.deletion
import inventory.models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0006_itemimages_inventoryitem_images'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inventoryitem',
            name='images',
        ),
        migrations.AlterField(
            model_name='itemimages',
            name='image',
            field=models.ImageField(upload_to=inventory.models.upload_to),
        ),
        migrations.AlterField(
            model_name='itemimages',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='inventory.inventoryitem'),
        ),
    ]
