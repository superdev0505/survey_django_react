# Generated by Django 2.0.6 on 2019-03-10 22:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0004_auto_20190310_2003'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='provider',
            name='impression_limit',
        ),
        migrations.RemoveField(
            model_name='provider',
            name='postback_after_all_impressions',
        ),
        migrations.RemoveField(
            model_name='provider',
            name='views_per_impression',
        ),
    ]
