# Generated by Django 4.2.18 on 2025-01-23 14:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('otp_auth', '0005_rename_id_user_uuid'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='uuid',
        ),
        migrations.AddField(
            model_name='user',
            name='id',
            field=models.BigAutoField(auto_created=True, default=1, primary_key=True, serialize=False, verbose_name='ID'),
            preserve_default=False,
        ),
    ]
