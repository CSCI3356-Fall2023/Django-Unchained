# Generated by Django 4.2.7 on 2023-12-15 15:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EagleVision', '0003_alter_student_graduation_semester'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='level',
            field=models.CharField(default='none', max_length=255),
        ),
    ]