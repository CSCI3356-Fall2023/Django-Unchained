# Generated by Django 4.2.6 on 2023-12-06 23:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('EagleVision', '0004_alter_course_time_slots'),
    ]

    operations = [
        migrations.RenameField(
            model_name='course',
            old_name='day',
            new_name='days',
        ),
    ]
