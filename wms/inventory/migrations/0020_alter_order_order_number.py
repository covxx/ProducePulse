# Generated by Django 4.2.13 on 2024-08-19 18:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0019_alter_order_order_number_ordercustomerproductprice_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_number',
            field=models.CharField(default='e15f6e96c539', editable=False, max_length=12, unique=True),
        ),
    ]
