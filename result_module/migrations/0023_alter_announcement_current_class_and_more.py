# Generated by Django 4.2.10 on 2024-05-07 20:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('result_module', '0022_alter_staffs_address_alter_staffs_current_class_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='announcement',
            name='current_class',
            field=models.CharField(blank=True, choices=[('Form One', 'Form One'), ('Form Two', 'Form Two'), ('Form Three', 'Form Three'), ('Form Four', 'Form Four')], max_length=20),
        ),
        migrations.AlterField(
            model_name='students',
            name='current_class',
            field=models.CharField(blank=True, choices=[('Form One', 'Form One'), ('Form Two', 'Form Two'), ('Form Three', 'Form Three'), ('Form Four', 'Form Four')], max_length=20),
        ),
        migrations.AlterField(
            model_name='students',
            name='gender',
            field=models.CharField(blank=True, choices=[('male', 'Male'), ('female', 'Female')], max_length=100),
        ),
    ]
