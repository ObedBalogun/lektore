# Generated by Django 3.2.16 on 2024-01-31 09:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_transaction'),
    ]

    operations = [
        migrations.AddField(
            model_name='userverificationmodel',
            name='new_reset',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='userverificationmodel',
            name='new_verification',
            field=models.BooleanField(default=False),
        ),
    ]
