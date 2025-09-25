from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    auth0_id = serializers.CharField(read_only=True)  # Added Auth0 ID

    class Meta:
        model = User
        fields = [
            "id", "email", "phone", "first_name", "last_name",
            "role", "is_active", "is_staff", "password", "auth0_id",
        ]
        read_only_fields = ["id", "auth0_id"]

    def get_fields(self):
        fields = super().get_fields()
        request = self.context.get("request")

        if not request or not request.user.is_authenticated or not request.user.is_staff:
            fields["is_staff"].read_only = True
            fields["is_active"].read_only = True
            fields["role"].read_only = True

        return fields

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        request = self.context.get("request")

        if not request or not request.user.is_authenticated or not request.user.is_staff:
            rep.pop("is_staff", None)
            rep.pop("is_active", None)

        return rep

    def create(self, validated_data):
        password = validated_data.pop("password")

        request = self.context.get("request")
        if not request or not request.user.is_authenticated or not request.user.is_staff:
            validated_data["role"] = User.Role.BUYER

        auth0_id = validated_data.pop("auth0_id", None)

        user = User(**validated_data)
        if auth0_id:
            user.auth0_id = auth0_id
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        validated_data.pop("auth0_id", None)

        request = self.context.get("request")
        if not request or not request.user.is_staff:
            validated_data.pop("role", None)
            validated_data.pop("is_staff", None)
            validated_data.pop("is_active", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)


class TokenResponseSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    refresh_token = serializers.CharField()
    expires_in = serializers.IntegerField()
    refresh_expires_in = serializers.IntegerField()
    token_type = serializers.CharField()
    not_before_policy = serializers.IntegerField()
    session_state = serializers.CharField()
    scope = serializers.CharField()
