# Generated by Django 4.2.6 on 2023-12-04 02:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EagleVision', '0023_course_major'),
    ]

    operations = [
        migrations.AlterField(
            model_name='course',
            name='major',
            field=models.CharField(default='none', max_length=255),
        ),
    ]