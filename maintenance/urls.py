from collections import namedtuple
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("addBuilding", views.addBuilding, name="addBuilding"),
    path("buildings", views.buildings, name="buildings"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("userlist", views.userlist, name="userlist"),
    path("confirmUser/<int:user_id>", views.confirmUser, name="confirmUser"),
    path("teams", views.teams, name="teams"),
    path("createTeam", views.createTeam, name="createTeam"),
    path('populateTeam/<int:team_id>', views.populateTeam, name="populateTeam"),
    path('addUserToTeam', views.addUserToTeam, name="addUserToTeam"),
    path("removefromTeam", views.removefromTeam, name="removefromTeam"),
    path("deleteTeam/<int:team_id>", views.deleteTeam, name="deleteTeam"),
    path("createTask", views.createTask, name="createTask"),
    path('tasks', views.tasks, name="tasks"),
]