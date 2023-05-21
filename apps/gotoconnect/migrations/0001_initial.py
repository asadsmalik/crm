# Generated by Django 4.0.6 on 2022-10-06 15:32

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('tenants', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GoToConnectUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('access_token', models.CharField(max_length=255, verbose_name='access_token')),
                ('refresh_token', models.CharField(max_length=255, verbose_name='refresh_token')),
                ('line_id', models.CharField(blank=True, max_length=255, null=True, verbose_name='line_id')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tenants.tenant')),
                ('user_profile', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GoToConnectConfig',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('client_id', models.CharField(blank=True, max_length=255, null=True, verbose_name='client_id')),
                ('client_secret', models.CharField(blank=True, max_length=255, null=True, verbose_name='client_secret')),
                ('tenant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='tenants.tenant')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
