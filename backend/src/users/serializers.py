from rest_framework import serializers
from .models import User


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            "id", "email", "phone", "first_name", "last_name",
            "role", "is_active", "is_staff", "password",
        ]
        read_only_fields = ["id"]

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
        password = validated_data.pop("password", None)
        request = self.context.get("request")
        if not request or not request.user.is_authenticated or not request.user.is_staff:
            validated_data["role"] = User.Role.BUYER
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
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


class GoogleTokenSerializer(serializers.Serializer):
    access_token = serializers.CharField()
    id_token = serializers.CharField()
    expires_in = serializers.IntegerField()
    token_type = serializers.CharField()
    scope = serializers.CharField(required=False)
