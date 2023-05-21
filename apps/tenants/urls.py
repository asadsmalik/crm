from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.tenants.views import TenantViewSet

router = DefaultRouter()
router.register("admin", TenantViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
