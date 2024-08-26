# Generated by Django 4.2.13 on 2024-08-22 14:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0023_convert_order_number_to_int'),
    ]

    operations = [
        migrations.CreateModel(
            name='Lot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lot_number', models.CharField(max_length=255)),
                ('quantity_in', models.DecimalField(decimal_places=2, max_digits=10)),
                ('quantity_used', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('contact_info', models.TextField(blank=True)),
            ],
        ),
        migrations.AddField(
            model_name='order',
            name='is_submitted',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='product',
            name='unit',
            field=models.CharField(choices=[('cases', 'Cases'), ('pounds', 'Pounds')], max_length=10),
        ),
        migrations.CreateModel(
            name='OrderItemLot',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity_used', models.DecimalField(decimal_places=2, max_digits=10)),
                ('lot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.lot')),
                ('order_item', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.orderitem')),
            ],
        ),
        migrations.AddField(
            model_name='lot',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='lots', to='inventory.product'),
        ),
        migrations.AddField(
            model_name='lot',
            name='vendor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='inventory.vendor'),
        ),
        migrations.AddField(
            model_name='orderitem',
            name='lots',
            field=models.ManyToManyField(through='inventory.OrderItemLot', to='inventory.lot'),
        ),
    ]
