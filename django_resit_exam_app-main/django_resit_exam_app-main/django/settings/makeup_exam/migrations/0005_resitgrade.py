# Generated by Django 5.1.5 on 2025-05-11 21:48

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('makeup_exam', '0004_coursesession'),
    ]

    operations = [
        migrations.CreateModel(
            name='ResitGrade',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('grade', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='Resit Exam Grade')),
                ('enrollment', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='resit_grade_entry', to='makeup_exam.enrollment', verbose_name='Enrollment for Resit')),
            ],
            options={
                'verbose_name': 'Resit Exam Grade',
                'verbose_name_plural': 'Resit Exam Grades',
            },
        ),
    ]
