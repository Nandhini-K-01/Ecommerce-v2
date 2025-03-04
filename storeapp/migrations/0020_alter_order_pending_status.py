# Generated by Django 4.2.18 on 2025-02-07 05:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('storeapp', '0019_order_payment_id_order_provider_order_id_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='pending_status',
            field=models.CharField(choices=[('P', 'Pending'), ('C', 'Complete'), ('F', 'Failed')], default='P', max_length=50),
        ),
    ]
