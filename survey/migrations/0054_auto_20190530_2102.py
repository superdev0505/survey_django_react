# Generated by Django 2.2 on 2019-05-30 21:02

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0053_auto_20190530_2056'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bannertype',
            name='size',
            field=django.contrib.postgres.fields.ArrayField(base_field=django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), size=2), default=list, size=4),
        ),
    ]
