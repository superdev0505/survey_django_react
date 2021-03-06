# Generated by Django 2.0.6 on 2019-03-27 22:41

from django.db import migrations, models
import django_countries.fields


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0014_auto_20190325_2231'),
    ]

    operations = [
        migrations.CreateModel(
            name='Price',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', django_countries.fields.CountryField(default='', max_length=2, verbose_name='country')),
                ('type', models.CharField(choices=[('desktop', 'desktop'), ('mobile', 'mobile')], default='desktop', max_length=8, verbose_name='type')),
                ('price', models.FloatField(blank=True, default=0.001, null=True, verbose_name='cycle price')),
            ],
        ),
    ]
