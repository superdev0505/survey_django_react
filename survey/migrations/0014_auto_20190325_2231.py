# Generated by Django 2.0.6 on 2019-03-25 22:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0013_surveyuser_provider_user_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='provider',
            name='currency',
            field=models.CharField(default='cents', max_length=8),
        ),
        migrations.AddField(
            model_name='surveyuser',
            name='ref_id',
            field=models.CharField(default='', max_length=8),
        ),
    ]
