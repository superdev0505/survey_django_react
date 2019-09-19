# Generated by Django 2.2.2 on 2019-06-20 06:00

from django.conf import settings
import django.contrib.postgres.fields
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0064_auto_20190616_1226'),
    ]

    operations = [
        migrations.CreateModel(
            name='Fingerprint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hash', models.CharField(max_length=256)),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('data', django.contrib.postgres.fields.jsonb.JSONField(default=dict)),
                ('userAgent', models.TextField(blank=True, default='', null=True)),
                ('language', models.TextField(blank=True, default='', null=True)),
                ('colorDepth', models.IntegerField(default=0)),
                ('deviceMemory', models.IntegerField(default=0)),
                ('hardwareConcurrency', models.IntegerField(default=0)),
                ('screenResolution', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), default=list, size=2)),
                ('availableScreenResolution', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), default=list, size=2)),
                ('timezoneOffset', models.IntegerField(default=0)),
                ('timezone', models.TextField(blank=True, default='', null=True)),
                ('sessionStorage', models.BooleanField(default=False)),
                ('localStorage', models.BooleanField(default=False)),
                ('indexedDb', models.BooleanField(default=False)),
                ('addBehavior', models.BooleanField(default=False)),
                ('openDatabase', models.BooleanField(default=False)),
                ('cpuClass', models.TextField(blank=True, default='', null=True)),
                ('platform', models.TextField(blank=True, default='', null=True)),
                ('plugins', django.contrib.postgres.fields.ArrayField(base_field=models.TextField(), default=list, size=None)),
                ('webglVendorAndRenderer', models.TextField(blank=True, default='', null=True)),
                ('adBlock', models.BooleanField(default=False)),
                ('hasLiedLanguages', models.BooleanField(default=False)),
                ('hasLiedResolution', models.BooleanField(default=False)),
                ('hasLiedOs', models.BooleanField(default=False)),
                ('hasLiedBrowser', models.BooleanField(default=False)),
                ('touchSupport', models.BooleanField(default=False)),
                ('fonts', django.contrib.postgres.fields.ArrayField(base_field=models.TextField(), default=list, size=None)),
                ('audio', models.TextField(blank=True, default='', null=True)),
            ],
        ),
        migrations.AddField(
            model_name='price',
            name='provider',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='survey.Provider'),
        ),
        migrations.CreateModel(
            name='UserFingerprint',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(default=django.utils.timezone.now)),
                ('fingerprint', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='survey.Fingerprint')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fingerprint', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddIndex(
            model_name='fingerprint',
            index=models.Index(fields=['hash'], name='survey_fing_hash_b20b4e_idx'),
        ),
        migrations.AddIndex(
            model_name='fingerprint',
            index=models.Index(fields=['hash', '-date'], name='survey_fing_hash_30866b_idx'),
        ),
        migrations.AddIndex(
            model_name='userfingerprint',
            index=models.Index(fields=['user'], name='survey_user_user_id_e895fe_idx'),
        ),
        migrations.AddIndex(
            model_name='userfingerprint',
            index=models.Index(fields=['user', '-date'], name='survey_user_user_id_67a0b1_idx'),
        ),
    ]
