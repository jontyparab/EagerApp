# Generated by Django 3.1.3 on 2021-08-04 19:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learnapp', '0009_auto_20210804_2307'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collection',
            name='posts',
            field=models.ManyToManyField(blank=True, to='learnapp.Post'),
        ),
    ]
