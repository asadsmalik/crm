# Generated by Django 4.0.6 on 2022-10-14 21:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0006_alter_userprofile_options'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userprofile',
            old_name='user_role',
            new_name='role',
        ),
    ]
