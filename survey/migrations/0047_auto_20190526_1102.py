# Generated by Django 2.2 on 2019-05-26 11:02

from decimal import Decimal
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0046_auto_20190522_0927'),
    ]

    operations = [
        migrations.AlterField(
            model_name='banner',
            name='device',
            field=models.CharField(choices=[('MOBILE', 'MOBILE'), ('DESKTOP', 'DESKTOP')], default='DESKTOP', max_length=32),
        ),
        migrations.AlterField(
            model_name='price',
            name='desktop',
            field=models.DecimalField(decimal_places=8, default=Decimal('0.0120000000000000002498001805406602215953171253204345703125'), max_digits=12),
        ),
        migrations.AlterField(
            model_name='price',
            name='mobile',
            field=models.DecimalField(decimal_places=8, default=Decimal('0.0120000000000000002498001805406602215953171253204345703125'), max_digits=12),
        ),
        migrations.AlterField(
            model_name='question',
            name='enabled',
            field=models.BooleanField(default=False),
        ),
    ]
