from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import LoginTokenObtainPairView

urlpatterns = [
    path("auth/token/", LoginTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
]
