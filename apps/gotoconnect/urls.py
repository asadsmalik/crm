from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.gotoconnect.views import GoToConnectView

router = DefaultRouter()
router.register("", GoToConnectView)

urlpatterns = [
    path("", include(router.urls)),
]
