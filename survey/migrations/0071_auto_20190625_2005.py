# Generated by Django 2.2.2 on 2019-06-25 20:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0070_auto_20190625_2004'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='PriceTMP',
            new_name='Price',
        ),
    ]
