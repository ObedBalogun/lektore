# Generated by Django 3.2.16 on 2023-12-01 08:14

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0008_auto_20230303_1450'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='educationalqualification',
            name='aspirations',
        ),
        migrations.AddField(
            model_name='educationalqualification',
            name='pending_qualifications',
            field=models.CharField(blank=True, default='', max_length=255, null=True, verbose_name='Pending Qualifications'),
        ),
        migrations.AlterField(
            model_name='course',
            name='tutor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tutor_courses', to='app.tutorprofile'),
        ),
        migrations.AlterField(
            model_name='schedule',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_schedule', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='CourseEnrollment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='course_enrollment', to='app.course')),
                ('tutee', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='tutee_course_class', to='app.tuteeprofile')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]