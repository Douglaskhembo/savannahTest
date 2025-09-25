from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from drf_spectacular.utils import extend_schema
from django.conf import settings
import requests

from .models import User
from .serializers import UserSerializer, LoginSerializer, TokenResponseSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ["register", "login"]:
            return [AllowAny()]
        elif self.action in ["list", "retrieve", "update", "partial_update", "destroy"]:
            return [IsAdminUser()]
        return super().get_permissions()

    # ----- Login (POST for Swagger/Postman) -----
    @extend_schema(
        request=LoginSerializer,
        responses={200: TokenResponseSerializer},
        description="Login with email & password to get Auth0 access token (Free Tier)"
    )
    @action(detail=False, methods=["post"], url_path="login", permission_classes=[AllowAny])
    def login(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        token_url = settings.OIDC_OP_TOKEN_ENDPOINT
        payload = {
            "grant_type": "password",
            "client_id": settings.OIDC_RP_CLIENT_ID,
            "client_secret": settings.OIDC_RP_CLIENT_SECRET,
            "username": email,
            "password": password,
            "audience": settings.AUTH0_AUDIENCE,
            "scope": "openid profile email",
            "realm": "Username-Password-Authentication",
        }

        resp = requests.post(token_url, json=payload)

        if resp.status_code != 200:
            return Response(
                {"detail": "Failed to authenticate with Auth0", "error": resp.json()},
                status=status.HTTP_403_FORBIDDEN
            )

        return Response(resp.json(), status=status.HTTP_200_OK)

    # ----- Helper: Get Management Token -----
    def get_management_token(self):
        url = f"https://{settings.AUTH0_DOMAIN}/oauth/token"
        payload = {
            "grant_type": "client_credentials",
            "client_id": settings.AUTH0_M2M_CLIENT_ID,
            "client_secret": settings.AUTH0_M2M_CLIENT_SECRET,
            "audience": settings.AUTH0_M2M_AUDIENCE,
        }
        resp = requests.post(url, json=payload)
        resp.raise_for_status()
        return resp.json()["access_token"]

    # ----- Register -----
    @extend_schema(
        request=UserSerializer,
        responses={201: UserSerializer},
        description="Register a new user via Auth0 and create local metadata"
    )
    @action(detail=False, methods=["post"], url_path="register", permission_classes=[AllowAny])
    def register(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            token = self.get_management_token()
        except Exception as e:
            return Response(
                {"detail": "Failed to get Auth0 Management API token", "error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        payload = {
            "email": serializer.validated_data["email"],
            "password": serializer.validated_data["password"],
            "connection": "Username-Password-Authentication",
            "given_name": serializer.validated_data.get("first_name", ""),
            "family_name": serializer.validated_data.get("last_name", ""),
        }

        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        resp = requests.post(
            f"https://{settings.AUTH0_DOMAIN}/api/v2/users",
            json=payload,
            headers=headers
        )

        if resp.status_code != 201:
            return Response(
                {"detail": "Failed to create user in Auth0", "error": resp.json()},
                status=status.HTTP_400_BAD_REQUEST
            )

        auth0_user = resp.json()
        user = serializer.save(auth0_id=auth0_user.get("user_id"))

        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
