# Generated by Django 4.2.18 on 2025-02-07 18:39

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('storeapp', '0021_alter_order_signature_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='SubscriptionPlan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('duration', models.IntegerField(help_text='Duration in days')),
                ('price', models.DecimalField(decimal_places=2, max_digits=6)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.AlterField(
            model_name='cartitems',
            name='cart',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='items', to='storeapp.cart'),
        ),
        migrations.AlterField(
            model_name='cartitems',
            name='product',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cartitems', to='storeapp.product'),
        ),
    ]
