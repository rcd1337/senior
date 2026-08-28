from django.urls import include, path

urlpatterns = [
    path("", include("guests.api.v1.urls")),
]
