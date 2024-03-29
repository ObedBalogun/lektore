# Generated by Django 4.2 on 2024-01-31 00:54

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('transaction_id', models.CharField(max_length=255)),
                ('amount', models.DecimalField(decimal_places=2, default=0.0, max_digits=19)),
                ('reference', models.CharField(max_length=255)),
                ('service_provider', models.CharField(max_length=255)),
                ('transaction_type', models.CharField(choices=[('debit', 'Debit'), ('credit', 'Credit')], default='debit', max_length=200)),
                ('status', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='user_transactions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
