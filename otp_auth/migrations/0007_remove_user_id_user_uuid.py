# Generated by Django 4.2.18 on 2025-01-23 14:28

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('otp_auth', '0006_remove_user_uuid_user_id'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='id',
        ),
        migrations.AddField(
            model_name='user',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True),
        ),
    ]
