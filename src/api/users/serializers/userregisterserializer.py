import re
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from src.apps.users.models import Users


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    username = serializers.CharField(max_length=150)

    class Meta:
        model = Users
        fields = ['username', 'email', 'password']

    def validate_username(self, value):
        # STRICT: Only letters and numbers. No @, no dots, no quotes.
        if not re.match(r'^[a-zA-Z0-9]+$', value):
            raise serializers.ValidationError(
                "Username must be alphanumeric (letters and numbers only)."
            )

        if len(value) < 4:
            raise serializers.ValidationError("Too short.")

        if Users.objects.filter(username__iexact=value).exists():
            raise serializers.ValidationError("Taken.")

        return value

    def validate_password(self, value):
        try:
            validate_password(value)
        except exceptions.ValidationError as e:
            raise serializers.ValidationError(list(e.messages))
        return value