# Generated by Django 3.2.5 on 2021-07-18 18:30

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('maintenance', '0005_auto_20210718_2249'),
    ]

    operations = [
        migrations.AlterField(
            model_name='building',
            name='coordinates',
            field=models.CharField(max_length=32, null=True),
        ),
        migrations.AlterField(
            model_name='maintenanceagreement',
            name='end_date',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2021, 7, 18, 23, 0, 11, 152030), null=True),
        ),
        migrations.AlterField(
            model_name='maintenanceagreement',
            name='start_date',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2021, 7, 18, 23, 0, 11, 152030), null=True),
        ),
        migrations.AlterField(
            model_name='task',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 18, 23, 0, 11, 152030)),
        ),
        migrations.AlterField(
            model_name='task',
            name='date',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 18, 23, 0, 11, 152030)),
        ),
        migrations.AlterField(
            model_name='userteam',
            name='created',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 18, 23, 0, 11, 152030)),
        ),
    ]
