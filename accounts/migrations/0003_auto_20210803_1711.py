# Generated by Django 3.1.3 on 2021-08-03 11:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_userprofile'),
    ]

    operations = [
        migrations.RenameField(
            model_name='userprofile',
            old_name='favourites',
            new_name='saved_posts',
        ),
    ]
