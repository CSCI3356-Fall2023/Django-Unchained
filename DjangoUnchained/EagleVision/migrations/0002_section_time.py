# Generated by Django 4.2.7 on 2023-12-06 21:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EagleVision', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='section',
            name='time',
            field=models.CharField(default='', max_length=255),
        ),
    ]