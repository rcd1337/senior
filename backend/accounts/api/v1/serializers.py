from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class LoginTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Login aceita username OU e-mail."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop(self.username_field)
        self.fields["login"] = serializers.CharField()

    def validate(self, attrs):
        login = attrs.pop("login")
        user = User.objects.filter(Q(username=login) | Q(email__iexact=login)).first()
        attrs[self.username_field] = user.username if user else login
        return super().validate(attrs)
