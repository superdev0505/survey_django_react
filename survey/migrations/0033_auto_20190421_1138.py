# Generated by Django 2.2 on 2019-04-21 11:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0032_auto_20190420_2046'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserFlags',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('key', models.CharField(max_length=8)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddIndex(
            model_name='userflags',
            index=models.Index(fields=['user'], name='survey_user_user_id_32f6f5_idx'),
        ),
        migrations.AddIndex(
            model_name='userflags',
            index=models.Index(fields=['user', '-date'], name='survey_user_user_id_703451_idx'),
        ),
    ]
