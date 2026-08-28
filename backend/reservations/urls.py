from django.urls import include, path

urlpatterns = [
    path("", include("reservations.api.v1.urls")),
]
