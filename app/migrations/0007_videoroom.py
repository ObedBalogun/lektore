# Generated by Django 4.2 on 2024-02-12 01:00

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0006_tuteeservice_remove_tuteeprofile_from_destination_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='VideoRoom',
            fields=[
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('room_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('room_name', models.CharField(max_length=128)),
                ('room_description', models.CharField(max_length=200)),
                ('duration', models.DateTimeField(null=True)),
                ('created_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='tutor_rooms', to='app.tutorprofile')),
                ('online_users', models.ManyToManyField(blank=True, to='app.tuteeprofile')),
            ],
            options={
                'abstract': False,
            },
        )
    ]
