# Generated by Django 2.0.6 on 2019-04-01 17:29

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0021_auto_20190401_0532'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usertransaction',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
