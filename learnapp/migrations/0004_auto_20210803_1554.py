# Generated by Django 3.1.3 on 2021-08-03 10:24

import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learnapp', '0003_auto_20210802_0045'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='postsgroup',
            name='tags',
        ),
        migrations.AlterField(
            model_name='post',
            name='tags',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.CharField(max_length=30, validators=[django.core.validators.RegexValidator(code='Enter a valid value.', message='Only lowercase alphanumeric, dash, space and hyphens are allowed.', regex='^[a-z0-9\\-_\\s]+$')]), blank=True, null=True, size=10),
        ),
    ]
