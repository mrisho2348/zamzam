# Generated by Django 4.2.10 on 2024-04-13 21:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('result_module', '0019_classattendance_studentclassattendance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='is_active',
            field=models.BooleanField(default=False),
        ),
    ]