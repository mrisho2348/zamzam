# Generated by Django 4.2.10 on 2024-03-25 21:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('result_module', '0009_alter_result_subject'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='studentsexaminfo',
            name='exam_type',
        ),
        migrations.RemoveField(
            model_name='studentsexaminfo',
            name='student',
        ),
        migrations.RemoveField(
            model_name='studentspositioninfo',
            name='exam_type',
        ),
        migrations.RemoveField(
            model_name='studentspositioninfo',
            name='student',
        ),
        migrations.DeleteModel(
            name='Results',
        ),
        migrations.DeleteModel(
            name='StudentsExamInfo',
        ),
        migrations.DeleteModel(
            name='StudentsPositionInfo',
        ),
    ]
