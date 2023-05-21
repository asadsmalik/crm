from django.contrib import admin

from apps.gotoconnect.models import GoToConnectConfig, GoToConnectUser

admin.site.register(GoToConnectConfig)
admin.site.register(GoToConnectUser)
