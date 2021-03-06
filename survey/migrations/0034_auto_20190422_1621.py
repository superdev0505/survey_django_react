# Generated by Django 2.2 on 2019-04-22 16:21

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0033_auto_20190421_1138'),
    ]

    operations = [
        migrations.AlterField(
            model_name='iphistory',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ip_history', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='userflags',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_flags', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name='userhistory',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_history', to=settings.AUTH_USER_MODEL),
        ),
    ]
