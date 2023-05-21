from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.profiles.views import UserLoginApiView, UserProfileViewSet

router = DefaultRouter()
router.register("profile", UserProfileViewSet)

urlpatterns = [
    path("login", UserLoginApiView.as_view(), name="login"),
    path("password_reset/", include("django_rest_passwordreset.urls", namespace="password_reset")),
    path("", include(router.urls)),
]
