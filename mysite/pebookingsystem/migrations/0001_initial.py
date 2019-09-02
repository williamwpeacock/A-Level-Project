# Generated by Django 2.0.2 on 2018-03-28 23:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('username', models.CharField(max_length=30, unique=True)),
                ('role', models.CharField(choices=[('A', 'Admin'), ('T', 'Teacher'), ('P', 'Parent'), ('S', 'Student')], default='Student', max_length=256)),
                ('pin', models.IntegerField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Admin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fullname', models.CharField(max_length=256)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Parent',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fullname', models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='ParentsEvening',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pename', models.CharField(max_length=256)),
                ('date', models.DateField()),
                ('starttime', models.TimeField()),
                ('endtime', models.TimeField()),
                ('appointmentlength', models.TimeField()),
            ],
        ),
        migrations.CreateModel(
            name='PEBooking',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timeslot', models.TimeField()),
                ('notes', models.TextField()),
                ('parentsevening', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pebookingsystem.ParentsEvening')),
            ],
        ),
        migrations.CreateModel(
            name='SchoolClass',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=256)),
                ('schoolyear', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fullname', models.CharField(max_length=256)),
                ('schoolyear', models.IntegerField()),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fullname', models.CharField(max_length=256)),
                ('title', models.CharField(max_length=10)),
                ('subject', models.CharField(max_length=256)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='schoolclass',
            name='students',
            field=models.ManyToManyField(to='pebookingsystem.Student'),
        ),
        migrations.AddField(
            model_name='schoolclass',
            name='teachers',
            field=models.ManyToManyField(to='pebookingsystem.Teacher'),
        ),
        migrations.AddField(
            model_name='pebooking',
            name='schoolclass',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pebookingsystem.SchoolClass'),
        ),
        migrations.AddField(
            model_name='pebooking',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pebookingsystem.Student'),
        ),
        migrations.AddField(
            model_name='parentsevening',
            name='schoolclasses',
            field=models.ManyToManyField(to='pebookingsystem.SchoolClass'),
        ),
        migrations.AddField(
            model_name='parent',
            name='children',
            field=models.ManyToManyField(to='pebookingsystem.Student'),
        ),
        migrations.AddField(
            model_name='parent',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
