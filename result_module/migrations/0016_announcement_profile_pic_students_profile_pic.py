# Generated by Django 4.2.10 on 2024-04-06 22:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('result_module', '0015_staffs_current_class'),
    ]

    operations = [
        migrations.AddField(
            model_name='announcement',
            name='profile_pic',
            field=models.FileField(blank=True, null=True, upload_to='announcement'),
        ),
        migrations.AddField(
            model_name='students',
            name='profile_pic',
            field=models.FileField(blank=True, null=True, upload_to='student_profile_pic'),
        ),
    ]
