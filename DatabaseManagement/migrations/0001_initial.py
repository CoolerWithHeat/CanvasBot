# Generated by Django 4.2.7 on 2024-03-09 18:50

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_id', models.IntegerField()),
                ('course_name', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('student_id', models.IntegerField()),
                ('student_token', models.CharField(max_length=255)),
                ('student_name', models.CharField(max_length=255)),
                ('previously_interacted', models.BooleanField(default=False)),
                ('courses', models.ManyToManyField(to='DatabaseManagement.course')),
            ],
        ),
    ]
