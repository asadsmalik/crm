# Generated by Django 4.0.6 on 2022-10-14 21:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0004_userprofile_manager'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userprofile',
            options={'permissions': (('list_userprofile', 'list user profiles'),)},
        ),
    ]
