from datetime import date, datetime
import json
from django.contrib.messages.api import warning
from django.core import exceptions
from django.core import validators
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, validate_email
from django.db.models.expressions import Subquery
from django.db.models.query_utils import Q
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
import requests


##### FORM CLASSES ########

# your desired format 
phone_regex = RegexValidator(
    regex=r'^(05)\d{9}$',
    message="Format must be like 05xxxxxxxxx",
)

class addBuildingForm(forms.Form):
    name = forms.CharField(label="Building Name", max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'style':'margin-bottom:15px;'}))
    address = forms.CharField(label="Building Address", max_length=300, widget=forms.Textarea(attrs={'class': 'form-control', 'style':'margin-bottom:15px;', 'rows':'2'}))
    manager = forms.CharField(label="Building Manager", max_length=100, widget=TextInput(attrs={'class':'form-control', 'style':'margin-bottom:15px;'}), required=False)
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
    first_name = forms.CharField(label="Firstname", max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'style':'margin-bottom:15px;'}))
    last_name = forms.CharField(label="Lastname", max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'style':'margin-bottom:15px;'}))
    email = forms.EmailField(label="Your e-mail",  max_length=100, widget=forms.EmailInput(attrs={'class':'form-control', 'style':'margin-bottom:15px;', 'type':'email'}))
    password = forms.CharField(label="Password", max_length=24, widget=forms.PasswordInput(attrs={'class':'form-control', 'style':'margin-bottom:15px;', 'type':'password'}))
    confirm = forms.CharField(label="Confirm your password", max_length=24, widget=forms.PasswordInput(attrs={'class':'form-control', 'style':'margin-bottom:15px;', 'type':'password'}))

class createTeamForm(forms.Form):
    leader = forms.ModelChoiceField(label="Choose e team leader", queryset=User.objects.filter(confirmed=True, is_active=True, is_staff=False).exclude(id__in=Subquery(UserTeam.objects.all().values_list('user_id', flat=True))), widget=forms.Select(attrs={'class': 'form-control', 'style':'margin-bottom:15px;'}))
    name = forms.CharField(label="Team name", max_length=50, widget=forms.TextInput(attrs={'class': 'form-control', 'style':'margin-bottom:15px;'}))
    description = forms.CharField(label="Description", max_length=200, widget=forms.Textarea(attrs={'class': 'form-control', 'style':'margin-bottom:15px;', 'rows':'2'}))
   

##### END OF FORM CLASSES ########
def index(request):
    user = request.user

    if user.is_anonymous:
        messages.warning(request, "Welcome! Please login or register")
        return render(request, "maintenance/index.html")

    #if user is confirmed
    #(first check if user is confirmed)
    if not user.confirmed:
        messages.warning(request, "Your registration not confirmed yet. Please try again later.")
        return render(request, "maintenance/index.html")
    
    #if user is staff
    #(show day's tasks, ongoing, completed and cancelled)
    if user.is_staff:
        # Below SELECT * FROM ..... WHERE .... OR ..... query stands
        tasks = Task.objects.filter(result__isnull=True) | Task.objects.filter(closed__date=date.today(), result__isnull=True) | Task.objects.filter(result=1, closed__date=date.today())
        return render(request, "maintenance/index.html", {
            "tasks":tasks,
        })

    #if user has a team
    #(show teams ongoing tasks)
    try:
        userTeam = UserTeam.objects.get(user_id = user.id)
        team = Team.objects.get(pk=userTeam.team_id)
        tasks = Task.objects.filter(team_id=team.id).exclude(closed__date__lt=date.today()).exclude(result=0) | Task.objects.filter(result=0, closed__date=date.today())
        return render(request, "maintenance/index.html", {
            "tasks":tasks,
        })
    except:
        messages.warning(request, "It seems you are not assigned to any team yet.")
        return render(request, "maintenance/index.html")
    
def register(request):
    if request.method == "POST":
       formRegisteration = registerationForm(request.POST)

       if formRegisteration.is_valid():
        # Ensure password matches confirmation
            password = formRegisteration.cleaned_data["password"]
            username = formRegisteration.cleaned_data["username"]
            first_name = formRegisteration.cleaned_data["first_name"]
            last_name = formRegisteration.cleaned_data["last_name"]
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

            users = User.objects.all()

            if email in users.values_list('email') or username in users.values_list('username'):
                messages.warning(request, "This email or username is already in use, please choose a different one.")
                return render(request, "maintenance/register.html", {
                    "formRegisteration": formRegisteration
                })

            # Attempt to create new user
            try:
                user = User.objects.create_user(username, email, password)
                user.first_name = first_name
                user.last_name = last_name
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
            if user.confirmed == True and user.is_active == True:
                login(request, user)
                user.last_login = datetime.now()
                user.save()
                #return render(request, "maintenance/index.html")
                return HttpResponseRedirect(reverse("index"))
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
def deActiveUser(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
    except:
        messages.warning(request, "No such user to active/deactive")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    userTeam = UserTeam.objects.filter(user_id=user_id)

    if len(userTeam) > 0:
        messages.warning(request, "This user is a member of a team, first remove him from team and try again.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    if user.is_active == False:     
        user.is_active = True
        messages.success(request, "User is activated successfully")
    else:
        user.is_active = False
        messages.success(request, "User is deactivated successfully")
    
    user.save()
    
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

@login_required
#Remove user completly from database
def removeUser(request, user_id):
    try:
        user = User.objects.get(pk=user_id)
    except:
        messages.warning(request, "No such user to deactivate")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    if user.is_active == True:
        messages.warning(request, "First deactivted this user and try again")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    user.delete()

    messages.success(request, "User is deleted successfully")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

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

            Yandex_Geocoder_API_KEY = "5cf6cfdf-b3b4-45be-92e2-9f3ee7a6c8fe"
            formatted_address = str(address).replace(" ", "+")
            Yandex_URL = f"https://geocode-maps.yandex.ru/1.x/?apikey={Yandex_Geocoder_API_KEY}&format=json&geocode={formatted_address}&lang=tr-TR"

            response = requests.get(Yandex_URL)
            geodata = response.json()

            point = geodata['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
            LongLat = point.split(' ')

            lastCoord = LongLat[1] + "," + LongLat[0]
    

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
                    building.coordinates = lastCoord
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
                "buildings": Building.objects.all()
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

    buildings = Building.objects.all()

    return render(request, "maintenance/buildings.html", {
        "buildings":buildings
    })

@login_required
def editBuilding(request, building_id):

    try:
        building = Building.objects.get(pk=building_id)
    except:
        messages.warning(request, "No such a building to edit")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    data = json.loads(request.body)

    name = body = data.get("name", "")
    address = body = data.get("address", "")
    manager = body = data.get("manager", "")
    phone = body = data.get("phone", "")
    email = body = data.get("email", "")
    floors = body = data.get("floors", "")
    elevator_type = body = data.get("elevator_type", "")
    status = body = data.get("status", "")

    if status == "False":
        status = False
    else:
        status = True

    oldAddress = building.address

    if status == False:
        tasks = Task.objects.filter(building_id = building.id, result__isnull=True)
        if len(tasks) > 0:
            return JsonResponse({"result":False, "message":"There are secheduled tasks for this building. Cancel those tasks and try again."}, status=500)

    try:
        with transaction.atomic():
            building.name = name
            building.address = address
            building.manager = manager
            building.phone = phone
            building.email = email
            building.floors = floors
            building.elevator_type = elevator_type
            building.status = status

            if oldAddress != address:
                Yandex_Geocoder_API_KEY = "5cf6cfdf-b3b4-45be-92e2-9f3ee7a6c8fe"
                formatted_address = str(address).replace(" ", "+")
                Yandex_URL = f"https://geocode-maps.yandex.ru/1.x/?apikey={Yandex_Geocoder_API_KEY}&format=json&geocode={formatted_address}&lang=tr-TR"

                response = requests.get(Yandex_URL)
                geodata = response.json()

                point = geodata['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
                LongLat = point.split(' ')

                lastCoord = LongLat[1] + "," + LongLat[0]
                building.coordinates = lastCoord

            building.save()
    except IntegrityError as e:
        #messages.warning(request, "Something went wrong, please try again.")
        return JsonResponse({"result":False, "message":"Something went wrong, please try again."}, status=500)

    return JsonResponse({"result":True, "message":"Building updated successfully"}, status=200)

@login_required
def deleteBuilding(request, building_id):
    try:
        building = Building.objects.get(pk=building_id)
    except:
        messages.warning(request, "No such a building to delete")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    tasks = Task.objects.filter(building_id=building.id)

    if len(tasks) > 0:
        messages.warning(request, "There are tasks on this building, cancel them and try again.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    building.delete()

    buildings = Building.objects.all()

    return render(request, "maintenance/buildings.html", {
        "buildings":buildings
    })

@login_required
def userlist(request):
    users = User.objects.exclude(is_staff=1).filter(is_active=1)
    
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
    
    deActiveUsers = User.objects.filter(is_active=0)
        
    return render(request, "maintenance/userlist.html", {
        "users": users,
        "deActiveUsers":deActiveUsers
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
        messages.warning(request, "You are not authorized.")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    teams = Team.objects.all()

    for f in teams:
        f.members = []

    members = UserTeam.objects.filter(role="member")
    suitableUsers = User.objects.filter(confirmed=True, is_active=True, is_staff=False).exclude(id__in=Subquery(UserTeam.objects.all().values_list('user_id', flat=True)))

    for m in members:
        if m.team in teams:
            for t in teams:
                if m.team == t:
                    t.members.append(m.user)

    return render(request, "maintenance/teams.html", {
        "teams":teams,
        "suitableUsers":suitableUsers,
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
            return HttpResponseRedirect('teams')
            # return render(request, "maintenance/teams.html", {
            #     "teams": Team.objects.all()
            # })
        else:
            return render(request, "maintenance/createTeam.html", {
                "teamForm": teamForm
            })

    else:
        return render(request, "maintenance/createTeam.html", {
            "teamForm": createTeamForm()
        })

@login_required
def editTeam(request, team_id):
    try:
        team = Team.objects.get(id=team_id)
    except:
        messages.warning(request, "No such a team to edit")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    data = json.loads(request.body)

    name = body = data.get("name", "")
    leader = body = data.get("leader", "")
    description = body = data.get("description", "")

    try:
        with transaction.atomic():
            team.name = name
            if team.leader.id != int(leader):
                userTeamOld = UserTeam.objects.get(user_id=team.leader.id)
                userTeamOld.delete()

                team.leader = User.objects.get(pk=int(leader))

                userTeamNew = UserTeam()
                userTeamNew.user = User.objects.get(pk=int(leader))
                userTeamNew.team = team
                userTeamNew.role = "leader"
                userTeamNew.created = datetime.now()
                userTeamNew.save()

            team.description = description
            team.save()
    except IntegrityError as e:
        return JsonResponse({"result":False, "message":"Something went wrong, please try again."}, status=500)

    return JsonResponse({"result":True, "message":"Team updated successfully"}, status=200)

@login_required
def populateTeam(request, team_id):

    try:
        team = Team.objects.get(id=team_id)
    except:
        return HttpResponse("No such e-a team exist")

    #Each user can be added to a single team so bring users who have not been added any
    alreadyAdded = UserTeam.objects.all().values_list('user_id', flat=True)
    users = User.objects.filter(is_active = True, is_staff=False)

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
    
    usersTeam = UserTeam.objects.filter(team_id=team.id, role="member")

    if len(usersTeam) > 0:
        messages.warning(request, "First, remove all members from team and try again")
        return HttpResponseRedirect(reverse("teams"))

    teamTasks = Task.objects.filter(team_id=team.id, result=None)

    if len(teamTasks) > 0:
        messages.warning(request, "This team has ongoing tasks, first cancel those tasks and try again.")
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
                        last_maintenance = Task.objects.filter(building_id=b.id, result=True).order_by('id').last()
                        b.task_status = t.date
                        b.task_team = t.team.name
                        b.task_type = t.type.type
                        if last_maintenance:
                            b.last = last_maintenance.closed
            else:
                for t in Task.objects.filter(building_id=b.id, result=True):
                    if b.id == t.building_id:
                        last_maintenance = Task.objects.filter(building_id=b.id, result=True).order_by('id').last()
                        if last_maintenance:
                            b.last = last_maintenance.closed

        
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
        tasks = Task.objects.filter(result=None).order_by("id").reverse()
    elif result == 1: # Completed tasks
        tasks = Task.objects.filter(result=True).order_by("id").reverse()
    elif result == 2: # Ongoing tasks
        tasks = Task.objects.filter(result=None).order_by("id").reverse()
    elif result == 3: # All tasks
        tasks = Task.objects.all().order_by("id").reverse()
    elif result == 4: # Cancelled tasks
        tasks = Task.objects.filter(result=False).order_by("id").reverse()
    else: # Ongoing tasks
        tasks = Task.objects.filter(result=None).order_by("id").reverse()

    

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

@login_required
def taskDone(request, task_id):
    
    try:
        task = Task.objects.get(pk=task_id)
    except:
        messages.warning(request, "No such a task to sign as completed")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    
    user = request.user

    if request.method == "GET":
        try:
            team = Team.objects.get(pk=task.team_id)
            userTeam = UserTeam.objects.get(user_id = user.id)
            if userTeam.user_id != user.id or userTeam.team_id != team.id:
                messages.warning(request, "You are not authorized to sign this task as completed")
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        except:
            messages.warning(request, "You are not authorized to sign this task as completed")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
        
        materials = Material.objects.all()

        return render(request, "maintenance/taskDone.html", {
            "task":task,
            "materials":materials
        })
    else:

        notes = request.POST["notes"]
        formMaterials = [int(i) for i in request.POST.getlist("materials")] 
        
        try:
            with transaction.atomic():
                task.notes = notes + f" < USER: ({request.user.id}) {request.user.first_name} {request.user.last_name} >" 
                for m in formMaterials:
                    mat = Material.objects.get(pk=m)
                    task.materials.add(mat)
                task.result = 1
                task.closed = datetime.now()
                task.save()
        except IntegrityError as e:
            messages.warning(request, "Something went wrong, please try again.")
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        return redirect('index')

@login_required
def buildingDetail(request, building_id):
    try:
        building = Building.objects.get(pk=building_id)
    except:
        messages.warning(request, "No such a building")
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    agreement = MaintenanceAgreement.objects.filter(building_id = building_id)

    tasks = Task.objects.filter(building_id = building_id)

    return render(request, "maintenance/buildingDetail.html", {
        "building":building,
        "agreement":agreement,
        "tasks":tasks
    })
    



            
        
    

    




