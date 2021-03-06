# Generated by Django 2.2 on 2019-04-22 20:15

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0034_auto_20190422_1621'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserFeedback',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('type', models.CharField(max_length=8)),
                ('text', models.TextField()),
                ('fingerprint', models.TextField()),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='user_feedback', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddIndex(
            model_name='userfeedback',
            index=models.Index(fields=['user'], name='survey_user_user_id_4eaaf7_idx'),
        ),
        migrations.AddIndex(
            model_name='userfeedback',
            index=models.Index(fields=['user', '-date'], name='survey_user_user_id_949f62_idx'),
        ),
    ]
