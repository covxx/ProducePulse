# Generated by Django 4.2.13 on 2024-08-19 18:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0020_alter_order_order_number'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='unit',
            field=models.CharField(choices=[('cases', 'Cases'), ('pounds', 'Pounds')], default='cases', max_length=10),
        ),
        migrations.AlterField(
            model_name='order',
            name='order_number',
            field=models.CharField(default='f45c54492847', editable=False, max_length=12, unique=True),
        ),
    ]
