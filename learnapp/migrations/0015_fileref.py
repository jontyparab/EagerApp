# Generated by Django 3.1.3 on 2021-09-22 20:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learnapp', '0014_post_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='FileRef',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=254)),
                ('url', models.URLField()),
            ],
        ),
    ]
