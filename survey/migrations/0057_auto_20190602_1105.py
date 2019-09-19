from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('survey', '0056_auto_20190602_1045'),
    ]

    operations = [
        migrations.RunSQL("CREATE INDEX index_name ON survey_questionanswer_choice (id)")
    ]
