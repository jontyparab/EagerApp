# Generated by Django 3.1.3 on 2021-08-03 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learnapp', '0006_auto_20210803_1711'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vote',
            name='vote',
            field=models.IntegerField(choices=[(-1, 'Down Vote'), (1, 'Up Vote')]),
        ),
    ]
