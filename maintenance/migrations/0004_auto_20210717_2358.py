# Generated by Django 3.2.5 on 2021-07-17 19:28

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maintenance', '0003_auto_20210717_2045'),
    ]

    operations = [
        migrations.AlterField(
            model_name='maintenanceagreement',
            name='end_date',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2021, 7, 17, 23, 58, 12, 625167), null=True),
        ),
        migrations.AlterField(
            model_name='maintenanceagreement',
            name='start_date',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2021, 7, 17, 23, 58, 12, 625167), null=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 17, 23, 58, 12, 625167)),
        ),
        migrations.AlterField(
            model_name='task',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 17, 23, 58, 12, 625167)),
        ),
        migrations.AlterField(
            model_name='task',
            name='materials',
            field=models.ManyToManyField(blank=True, null=True, related_name='materials', to='maintenance.Material'),
        ),
        migrations.AlterField(
            model_name='userteam',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 17, 23, 58, 12, 625167)),
        ),
    ]
