# Generated by Django 4.2.18 on 2025-02-14 05:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('otp_auth', '0011_user_is_subscription_active_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='subscription_end_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='subscription_start_date',
            field=models.DateField(blank=True, null=True),
        ),
    ]
