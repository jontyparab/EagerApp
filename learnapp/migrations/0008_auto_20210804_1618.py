# Generated by Django 3.1.3 on 2021-08-04 10:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learnapp', '0007_auto_20210803_1843'),
    ]

    operations = [
        migrations.AlterField(
            model_name='collection',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='post',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
