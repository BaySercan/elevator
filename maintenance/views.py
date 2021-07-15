from datetime import datetime
import json
from django.core import exceptions
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.forms.forms import Form
from django.forms.widgets import TextInput
from django.shortcuts import redirect, render
from django.contrib.auth import authenticate, login, logout, password_validation
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect, request
from django.http.response import JsonResponse
from django.urls import reverse
from django.template.defaulttags import register
from .models import Building, Team, User, UserTeam, MaintenanceAgreement, MaintenanceCycles, MaintenanceSchedule, Material, Task, AgreementTypes, TaskTypes
from django import forms
from django.db import transaction, IntegrityError
from django.contrib import messages


##### FORM CLASSES ########

class addBuildingForm(forms.Form):
    name = forms.CharField(label="Building Name", max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'style':'margin-bottom:15px;'}))
    address = forms.CharField(label="Building Address", max_length=300, widget=forms.Textarea(attrs={'class': 'form-control', 'style':'margin-bottom:15px;', 'rows':'2'}))
    manager = forms.CharField(label="Building Manager", max_length=100, widget=TextInput(attrs={'class':'form-control', 'style':'margin-bottom:15px;'}), required=False)
    
    # your desired format 
    phone_regex = RegexValidator(
        regex=r'^(05)\d{9}$',
        message="Format must be like 05xxxxxxxxx",
    )

    phone = forms.CharField(label="Manager Phone Number", max_length=11, widget=forms.NumberInput(attrs={'class':'form-control', 'style':'margin-bottom:15px;', 'type':'phone'}), validators=[phone_regex], required=False)
    email = forms.EmailField(label="Manager E-mail Address", max_length=100, widget=forms.EmailInput(attrs={'class':'form-control', 'style':'margin-bottom:15px;', 'type':'email'}), required=False)
    floors = forms.IntegerField(label="How many floors?", max_value=25, min_value=2, widget=forms.NumberInput(attrs={'class':'form-control', 'style':'margin-bottom:15px;'}), required=False)
    elevator_type = forms.CharField(label="Elevator Type", max_length=100, widget=forms.TextInput(attrs={'class':'form-control', 'style':'margin-bottom:15px;'}), required=False)
    #status = forms.BooleanField(label="Is Building Active?", widget=forms.RadioSelect(attrs={'class':'form-sontrol', 'style':'margin-bottom:15px;'}))

    #While adding a new building, aggrement information will also be taken from user
    agreement_type = forms.ModelChoiceField(label="Agreement Type", queryset=AgreementTypes.objects.all(), widget=forms.Select(attrs={'class': 'form-control', 'style':'margin-bottom:15px;'}), required=False)
    start_date = forms.DateTimeField(label="Start of Agreement", widget=forms.DateTimeInput(attrs={'class':'form-control', 'style':'margin-bottom:15px;', 'type':'date'}), required=False)
    end_date = forms.DateTimeField(label="End of Agreement", widget=forms.DateTimeInput(attrs={'class':'form-control', 'style':'margin-bottom:15px;', 'type':'date'}), required=False)
    
#Any new agreement for an existing building, this for will be in use
class addMaintenanceAggreementForm(forms.Form):
    agreement_type = forms.ModelChoiceField(label="Agreement Type", queryset=AgreementTypes.objects.all(), widget=forms.Select(attrs={'class': 'form-control', 'style':'margin-bottom:15px;'}), required=False)
    start_date = forms.DateTimeField(label="Start of Agreement", widget=forms.DateTimeInput(attrs={'class':'form-control', 'style':'margin-bottom:15px;'}), required=False)
    end_date = forms.DateTimeField(label="End of Agreement", widget=forms.DateTimeInput(attrs={'class':'form-control', 'style':'margin-bottom:15px;'}), required=False)

class registerationForm(forms.Form):
    username = forms.CharField(label="Username", max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'style':'margin-bottom:15px;'}))
    email = forms.EmailField(label="Your e-mail",  max_length=100, widget=forms.EmailInput(attrs={'class':'form-control', 'style':'margin-bottom:15px;', 'type':'email'}))
    password = forms.CharField(label="Password", max_length=24, widget=forms.PasswordInput(attrs={'class':'form-control', 'style':'margin-bottom:15px;', 'type':'password'}))
    confirm = forms.CharField(label="Confirm your password", max_length=24, widget=forms.PasswordInput(attrs={'class':'form-control', 'style':'margin-bottom:15px;', 'type':'password'}))

class createTeamForm(forms.Form):
    leader = forms.ModelChoiceField(label="Choose e team leader", queryset=User.objects.filter(confirmed=True), widget=forms.Select(attrs={'class': 'form-control', 'style':'margin-bottom:15px;'}))
    name = forms.CharField(label="Team name", max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'style':'margin-bottom:15px;'}))
    description = forms.CharField(label="Description", max_length=200, widget=forms.Textarea(attrs={'class': 'form-control', 'style':'margin-bottom:15px;', 'rows':'2'}))
   

##### END OF FORM CLASSES ########
def index(request):
    return render(request, "maintenance/index.html")


def register(request):
    if request.method == "POST":
       formRegisteration = registerationForm(request.POST)

       if formRegisteration.is_valid():
        # Ensure password matches confirmation
            password = formRegisteration.cleaned_data["password"]
            username = formRegisteration.cleaned_data["username"]
            email = formRegisteration.cleaned_data["email"]
            confirm = formRegisteration.cleaned_data["confirm"]

            ###########OPEN AT GIT PUSH###################################
            """try:
                password_validation.validate_password(password)
            except exceptions.ValidationError as v:
                for e in v.error_list:
                     messages.add_message(request, messages.WARNING, e)

                return render(request, "maintenance/register.html", {
                    "formRegisteration": formRegisteration
                })"""
            ############################################################33
                
            if password != confirm:
                messages.warning(request, "Your password and confirmation password does not match!")
                return render(request, "maintenance/register.html", {
                    "formRegisteration": formRegisteration
                })

            # Attempt to create new user
            try:
                user = User.objects.create_user(username, email, password)
                user.save()
            except IntegrityError as e:
                messages.warning(request, e.__cause__)
                return render(request, "maintenance/register.html", {
                    "formRegisteration": formRegisteration
                })

            #login(request, user)
            messages.success(request, 'You have successfully registered, now wait for confirmation by your supervisor.')
            return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "maintenance/register.html", {
            "formRegisteration": registerationForm()
        })

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            if user.confirmed == True:
                login(request, user)
                return render(request, "maintenance/index.html")
            else:
                messages.warning(request, "Your supervisor have not confirmed your account yet.")
                return render(request, "maintenance/login.html")
        else:
            messages.warning(request, "Invalid username or password")
            return render(request, "maintenance/login.html")
    else:
        return render(request, "maintenance/login.html")

@login_required
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

@login_required
#@transaction.atomic
def addBuilding(request):
    if request.method == "POST":
        formBuilding = addBuildingForm(request.POST)

        if formBuilding.is_valid():
            name = formBuilding.cleaned_data["name"]
            address = formBuilding.cleaned_data["address"]
            manager = formBuilding.cleaned_data["manager"]
            phone = formBuilding.cleaned_data["phone"]
            email = formBuilding.cleaned_data["email"]
            floors = formBuilding.cleaned_data["floors"]
            elevator_type = formBuilding.cleaned_data["elevator_type"]

            agreement_type = formBuilding.cleaned_data["agreement_type"]
            start_date = formBuilding.cleaned_data["start_date"]
            end_date = formBuilding.cleaned_data["end_date"]

            try:
                with transaction.atomic():
                    building = Building()
                    building.name = name
                    building.address = address
                    building.manager = manager
                    building.phone = phone
                    building.email = email
                    building.floors = floors
                    building.elevator_type = elevator_type
                    building.status = True
                    building.creator = request.user
                    building.save()

                    agreement = MaintenanceAgreement()
                    agreement.type = agreement_type
                    agreement.start_date = start_date
                    agreement.end_date = end_date
                    agreement.building = building
                    agreement.save()

            except IntegrityError as e:
                messages.warning(request, 'Something went wrong please try again.' + ' ' + e.__cause__)
                return render(request, "maintenance/addbuilding.html", {
                    "addBuildingForm": formBuilding
                })

            messages.success(request, 'You have successfully added new building.')
            return render(request, "maintenance/buildings.html", {
                "buildings": Building.objects.filter(status = True)
            })
        else:
            messages.warning(request, 'Something went wrong please try again.')
            return render(request, "maintenance/addbuilding.html", {
                "addBuildingForm": formBuilding
            })
            
    else:
        return render(request, "maintenance/addbuilding.html", {
                "addBuildingForm": addBuildingForm()
            })

@login_required
def buildings(request):

    buildings = Building.objects.filter(status=True)

    return render(request, "maintenance/buildings.html", {
        "buildings":buildings
    })

@login_required
def userlist(request):

    users = User.objects.all()

    for u in users:
        try:
            userTeam = UserTeam.objects.get(user_id = u.id)
            if userTeam:
                try:
                    team = Team.objects.get(pk=userTeam.team_id)
                    u.team = team.name
                except:
                    pass
        except:
            pass
        
    return render(request, "maintenance/userlist.html", {
        "users": users
    })

@login_required
def confirmUser(request, user_id):
    try:
        user = User.objects.get(id=user_id)
    except:
        msg = "No such user registered."
        return JsonResponse({"result":False, "message":msg}, status=404)
    
    if request.user.is_staff != 1:
        return JsonResponse({"result":False, "message":"You are not authorized to confirm or unconfirm a user."}, status=403)

    if user.confirmed == 0:
        user.confirmed = 1
    else:
        user.confirmed = 0
    
    user.save()

    msg = "You have successfully change the user's confirmation status."
    return JsonResponse({"result":True, "message":msg})

@login_required
def teams(request):

    if request.user.is_staff != 1:
        messages.warning(request, "You are not authorized to confirm or unconfirm a user.")
        return reverse(request)

    teams = Team.objects.all()

    for f in teams:
        f.members = []

    members = UserTeam.objects.filter(role="member")

    for m in members:
        if m.team in teams:
            for t in teams:
                if m.team == t:
                    t.members.append(m.user)

    return render(request, "maintenance/teams.html", {
        "teams":teams
    })

@login_required
def createTeam(request):

    if request.method == "POST":
        teamForm = createTeamForm(request.POST)

        if teamForm.is_valid():

            leader = teamForm.cleaned_data["leader"]
            name = teamForm.cleaned_data["name"]
            description = teamForm.cleaned_data["description"]
            
            if len(UserTeam.objects.filter(user=leader)) > 0:
                messages.warning(request, 'Leader has already joined a team, choose a different user.')
                return render(request, "maintenance/createTeam.html", {
                     "teamForm": teamForm
                })
                

            try:
                with transaction.atomic():
                    newTeam = Team()
                    newTeam.leader = leader
                    newTeam.name = name
                    newTeam.description = description
                    newTeam.save()

                    leaderTeam = UserTeam()
                    leaderTeam.user = leader
                    leaderTeam.team = newTeam
                    leaderTeam.role = "leader"
                    leaderTeam.created = datetime.now()
                    leaderTeam.save()

            except IntegrityError as e:
                messages.warning(request, 'Something went wrong please try again.' + ' ' + e.__cause__)
                return render(request, "maintenance/createTeam.html", {
                    "teamForm": teamForm
                })

            messages.success(request, "You have successfully created a new team")
            return render(request, "maintenance/teams.html", {
                "teams": Team.objects.all()
            })
        else:
            return render(request, "maintenance/createTeam.html", {
                "teamForm": teamForm
            })

    else:
        return render(request, "maintenance/createTeam.html", {
            "teamForm": createTeamForm()
        })

@login_required
def populateTeam(request, team_id):

    try:
        team = Team.objects.get(id=team_id)
    except:
        return HttpResponse("No such e-a team exist")

    #Each user can be added to a single team so bring users who have not been added any
    alreadyAdded = UserTeam.objects.all().values_list('user_id', flat=True)
    users = User.objects.filter(is_active = True)

    suitableUsers = User.objects.none()

    for u in users:
        if not u.id in alreadyAdded:
            suitableUsers |= User.objects.filter(pk=u.id)
    
    return render(request, "maintenance/populateTeam.html", {
        "suitableUsers":suitableUsers,
        "team": team
    })

@login_required
def addUserToTeam(request):
    if request.method != "PUT":
        return JsonResponse({"result":False, "message":"Request type must be 'PUT'"})

    data = json.loads(request.body)

    team_id = data.get("team_id", "")
    user_id = data.get("user_id", "")

    try:
        team = Team.objects.get(pk=team_id)
        user = User.objects.get(pk=user_id)
    except:
        return JsonResponse({"result":False, "message":"Something went wrong, plase try again."})
    

    if UserTeam.objects.filter(user_id = user.id):
        return JsonResponse({"result":False, "message":"This user is already a member of a team"})

    try:
        with transaction.atomic():
            newMember = UserTeam()
            newMember.user = user
            newMember.team = team
            newMember.created = datetime.now()
            newMember.save()
    except IntegrityError as e:
        return JsonResponse({"result":False, "message":"Something went wrong, plase try again."})

    return JsonResponse({"result":True, "message":"You have successfully added this user to team " + team.name})

@login_required
def removefromTeam(request):
    if request.method != "PUT":
        return JsonResponse({"result":False, "message":"Request type must be 'PUT'"})
    
    data = json.loads(request.body)

    team_id = data.get("team_id", "")
    user_id = data.get("user_id", "")

    try:
        team = Team.objects.get(pk=team_id)
        user = User.objects.get(pk=user_id)
        userteam = UserTeam.objects.filter(user_id=user.id, team_id=team.id)
    except:
        return JsonResponse({"result": False, "message":"Something went wrong, please try again"})
    
    try:
        with transaction.atomic():
            userteam.delete()
    except IntegrityError as e:
         return JsonResponse({"result": False, "message": "Something went wrong, please try again"})
       
    
    return JsonResponse({"result": True, "message": "You have successfully removed the user from team"})
    
@login_required
def deleteTeam(request, team_id):
    try:
        team = Team.objects.get(pk=team_id)
    except:
        messages.warning(request, "No such team to delete.")
        return HttpResponseRedirect(reverse("teams"))
    
    usersTeam = UserTeam.objects.filter(team_id=team.id)

    if len(usersTeam) > 0:
        messages.warning(request, "First, remove all members from team and try again")
        return HttpResponseRedirect(reverse("teams"))

    try:
        with transaction.atomic():
            team.delete()
    except IntegrityError as e:
        messages.warning(request, "Something went wrong please try again")
        return HttpResponseRedirect(reverse("teams"))

    return render(request, "maintenance/teams.html", {
        "teams":Team.objects.all()
    })

@login_required
def createTask(request):

    if request.method == "GET":
        buildings = Building.objects.filter(status=True)
        teams = Team.objects.all()

        if not len(buildings) > 0 or not len(teams) > 0:
            messages.warning(request, "First add buildings and create teams to assign a new task")
            if not len(buildings) > 0:
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
            elif  not len(teams) > 0:
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        tasks = Task.objects.filter(result=None)
        
        for f in teams:
            f.members = []

        members = UserTeam.objects.filter(role="member")

        for m in members:
            if m.team in teams:
                for t in teams:
                    if m.team == t:
                        t.members.append(m.user)

        

        for b in buildings:
            if b.id in tasks.values_list("building_id", flat=True):
                for t in tasks:
                    if b.id == t.building_id:
                        last_maintenance = Task.objects.filter(building_id=b.id, result=True).last()
                        b.task_status = t.date
                        b.task_team = t.team.name
                        b.task_type = t.type.type
                        b.last = last_maintenance
        
        taskTypes = TaskTypes.objects.all()

        return render(request, "maintenance/createTask.html", {
            "buildings":buildings,
            "teams":teams,
            "taskTypes":taskTypes,
        })
    else:

        building_id = request.POST["building"]
        team_id = request.POST["team"]
        description = request.POST["description"]
        type_id = request.POST["taskType"]
        date = request.POST['date']

        if date == "":
            messages.warning(request, "Choose valid date for the task")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        try:
            building = Building.objects.get(pk=building_id)
            team = Team.objects.get(pk=team_id)
            type = TaskTypes.objects.get(pk=type_id)
        except:
            messages.warning(request, "No such building or team.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        try:
            with transaction.atomic():
                newTask = Task()
                newTask.building = building
                newTask.team = team
                newTask.description = description
                newTask.type = type
                newTask.date = date
                newTask.created = datetime.now()
                newTask.save()
        except IntegrityError as e:
            messages.warning(request, "Something went wrong, please try again.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        #return render(request, "maintenance/tasks.html")
        return HttpResponseRedirect('tasks')
        
@login_required
def tasks(request, result=2):
    if result == 0: # Ongoing tasks
        tasks = Task.objects.filter(result=None)
    elif result == 1: # Completed tasks
        tasks = Task.objects.filter(result=True)
    elif result == 2: # Ongoing tasks
        tasks = Task.objects.filter(result=None)
    elif result == 3: # All tasks
        tasks = Task.objects.all()
    elif result == 4: # Cancelled tasks
        tasks = Task.objects.filter(result=False)
    else: # Ongoing tasks
        tasks = Task.objects.filter(result=None)


    return render(request, "maintenance/tasks.html", {
            "tasks": tasks,
        })

@login_required
def cancelTask(request, task_id):

    try:
        task = Task.objects.get(pk=task_id)
    except:
        messages.warning(request, "No such a task to cancel")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))


    try:
        with transaction.atomic():
            task.closed = datetime.now()
            task.result = False
            task.save()
    except IntegrityError as e:
        messages.warning(request, "Something went wrong please try again")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return redirect('tasks')


            
        
    

    




