# Generated by Django 3.2.4 on 2021-07-14 19:47

import datetime
from django.conf import settings
import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('confirmed', models.BooleanField(default=False)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='AgreementTypes',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='Building',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=300)),
                ('name', models.CharField(max_length=50)),
                ('manager', models.CharField(max_length=100)),
                ('phone', models.CharField(blank=True, max_length=11, null=True, validators=[django.core.validators.RegexValidator(message='Phone number must be entered in the format: 05xxxxxxxxx', regex='^(05)\\d{9}$')])),
                ('email', models.EmailField(blank=True, max_length=100, null=True)),
                ('floors', models.PositiveSmallIntegerField(default=2, validators=[django.core.validators.MinValueValidator(2), django.core.validators.MaxValueValidator(25)])),
                ('elevator_type', models.CharField(max_length=100)),
                ('status', models.BooleanField(default=True)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='BuildingCreator', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='MaintenanceCycles',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cycle', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Material',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('in_stock', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('description', models.CharField(max_length=200)),
                ('leader', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='team_leader', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='UserTeam',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(default='member', max_length=8)),
                ('created', models.DateTimeField(default=datetime.datetime(2021, 7, 15, 0, 17, 35, 950047))),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='maintenance.team')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='team_members', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.CharField(blank=True, max_length=200, null=True)),
                ('date', models.DateTimeField(default=datetime.datetime(2021, 7, 15, 0, 17, 35, 955059))),
                ('created', models.DateTimeField(default=datetime.datetime(2021, 7, 15, 0, 17, 35, 955059))),
                ('updated', models.DateTimeField(blank=True, null=True)),
                ('result', models.BooleanField(blank=True, null=True)),
                ('closed', models.DateTimeField(blank=True, null=True)),
                ('notes', models.CharField(blank=True, max_length=400, null=True)),
                ('building', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='maintenance.building')),
                ('material', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='maintenance.material')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='maintenance.team')),
            ],
        ),
        migrations.CreateModel(
            name='MaintenanceSchedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_maintenance', models.DateTimeField()),
                ('next_maintenance', models.DateTimeField()),
                ('building', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='maintenance.building')),
                ('cycle', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='maintenance.maintenancecycles')),
            ],
        ),
        migrations.CreateModel(
            name='MaintenanceAgreement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_date', models.DateTimeField(blank=True, default=datetime.datetime(2021, 7, 15, 0, 17, 35, 955059), null=True)),
                ('end_date', models.DateTimeField(blank=True, default=datetime.datetime(2021, 7, 15, 0, 17, 35, 955059), null=True)),
                ('building', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='maintenance.building')),
                ('type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='maintenance.agreementtypes')),
            ],
        ),
    ]