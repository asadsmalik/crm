# Generated by Django 4.0.6 on 2022-10-14 21:45

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0005_alter_userprofile_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='userprofile',
            options={'permissions': (('list_userprofile', 'Can list user profiles'),)},
        ),
    ]
