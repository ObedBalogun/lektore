# Generated by Django 4.2 on 2024-02-04 22:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_rename_tuteeorder_courseorder_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tuteeprogress',
            name='module',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='tutee_completion', to='app.module'),
        ),
    ]
