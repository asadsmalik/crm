from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.roles.views import RoleViewSet

router = DefaultRouter()
router.register("roles", RoleViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
