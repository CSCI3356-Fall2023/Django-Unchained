# Generated by Django 5.0 on 2023-12-05 05:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EagleVision', '0002_watchlist_section'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='max_students_on_watch',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='course',
            name='min_students_on_watch',
            field=models.IntegerField(default=0),
        ),
    ]