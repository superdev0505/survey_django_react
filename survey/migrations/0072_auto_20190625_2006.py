# Generated by Django 2.2.2 on 2019-06-25 20:06

from django.db import migrations
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0071_auto_20190625_2005'),
    ]

    operations = [
        migrations.AlterField(
            model_name='price',
            name='country',
            field=django_countries.fields.CountryField(blank=True, default='', max_length=2, null=True),
        ),
    ]
