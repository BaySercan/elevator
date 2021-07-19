import re
from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import datetime
from django.db.models.deletion import CASCADE, PROTECT
from django.core.validators import MinValueValidator, RegexValidator, MaxValueValidator

class TaskTypes(models.Model):
    type = models.CharField(max_length=32)

    def __str__(self) -> str:
        return self.type

class AgreementTypes(models.Model):
    type= models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.type

#weekly, monthly, every 3 months, every 6 months, yearly etc.
class MaintenanceCycles(models.Model):
    cycle = models.CharField(max_length=50)

    def __str__(self) -> str:
        return self.cycle

class User(AbstractUser):
    confirmed = models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.first_name + " " + self.last_name + " (" + self.username + ")"

class Building(models.Model):
    address = models.CharField(max_length=300)
    coordinates = models.CharField(null=True, max_length=32)
    name = models.CharField(max_length=50)
    manager = models.CharField(max_length=100)

    # error message when a wrong format entered
    phone_message = 'Phone number must be entered in the format: 05xxxxxxxxx' 

     # your desired format 
    phone_regex = RegexValidator(
        regex=r'^(05)\d{9}$',
        message=phone_message
    )

    # finally, your phone number field
    phone = models.CharField(validators=[phone_regex], max_length=11,
                             null=True, blank=True)

    email = models.EmailField(null=True, blank=True, max_length=100)
    
    floors = models.PositiveSmallIntegerField(default=2, validators=[MinValueValidator(2), MaxValueValidator(25)])
    elevator_type = models.CharField(max_length=100)
    creator = models.ForeignKey(User, on_delete=PROTECT, related_name="BuildingCreator")
    status = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name + ": İletişim: " + self.manager + " Tel: " + self.phone 

class Team(models.Model):
    leader = models.ForeignKey(User, on_delete=models.CASCADE, related_name="team_leader")
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=200)

    def __str__(self) -> str:
        return self.name + " => " + self.leader.first_name + " " + self.leader.last_name
    
class UserTeam(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="team_members")
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    role = models.CharField(max_length=8, default="member")
    created = models.DateTimeField(default=datetime.now())

    def __str__(self) -> str:
        return "User: " + self.user.id + "Team: " + self.team.id

class Material(models.Model):
    name = models.CharField(max_length=100)
    in_stock = models.BooleanField(default=True)

    def __str__(self) -> str:
        return self.name

class Task(models.Model):
    building = models.ForeignKey(Building, on_delete=CASCADE)
    team = models.ForeignKey(Team, on_delete=CASCADE)
    materials = models.ManyToManyField(Material, null=True, blank=True, related_name="materials")
    description = models.CharField(max_length=200, null=True, blank=True)
    date = models.DateTimeField(default=datetime.now())
    created = models.DateTimeField(default=datetime.now())
    updated = models.DateTimeField(null=True, blank=True)
    result = models.BooleanField(null=True, blank=True)
    closed = models.DateTimeField(null=True, blank=True)
    #team's notes about the task
    notes = models.CharField(max_length=400, null=True, blank=True)
    type = models.ForeignKey(TaskTypes, on_delete=PROTECT)

    def __str__(self) -> str:
        return self.building.name + " " + self.team.name + " " + self.created + " " + self.result

class MaintenanceAgreement(models.Model):
    building = models.ForeignKey(Building, on_delete=CASCADE)
    type = models.ForeignKey(AgreementTypes, on_delete=PROTECT, null=True, blank=True)
    start_date = models.DateTimeField(default=datetime.now(), null=True, blank=True)
    end_date = models.DateTimeField(default=datetime.now(), null=True, blank=True)

    def __str__(self) -> str:
        return self.building.name + " " + self.type.type + " " + self.start_date + " " + self.end_date

class MaintenanceSchedule(models.Model):
    building = models.ForeignKey(Building, on_delete=CASCADE)
    cycle = models.ForeignKey(MaintenanceCycles, on_delete=PROTECT)
    last_maintenance = models.DateTimeField()
    next_maintenance = models.DateTimeField()

    def __str__(self) -> str:
        return self.building.name + " " + self.cycle.cycle + " " + self.last_maintenance




