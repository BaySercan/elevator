from django.contrib import admin
from .models import Building, MaintenanceAgreement, MaintenanceCycles, Material, AgreementTypes, Task, MaintenanceSchedule, Team, User, UserTeam, TaskTypes
# Register your models here.
admin.site.register(Building)
admin.site.register(MaintenanceAgreement)
admin.site.register(MaintenanceCycles)
admin.site.register(MaintenanceSchedule)
admin.site.register(Material)
admin.site.register(AgreementTypes)
admin.site.register(Task)
admin.site.register(TaskTypes)
admin.site.register(Team)
admin.site.register(UserTeam)
admin.site.register(User)
