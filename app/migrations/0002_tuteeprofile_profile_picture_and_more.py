# Generated by Django 4.1.4 on 2022-12-12 22:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tuteeprofile',
            name='profile_picture',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='tutorprofile',
            name='profile_picture',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
