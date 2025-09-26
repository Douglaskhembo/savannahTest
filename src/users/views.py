from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from drf_spectacular.utils import extend_schema
from django.conf import settings
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import requests
import jwt

from .serializers import UserSerializer, GoogleTokenSerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ["register", "login"]:
            return [AllowAny()]
        elif self.action in ["list", "retrieve", "update", "partial_update", "destroy"]:
            return [IsAdminUser()]
        return super().get_permissions()

    @extend_schema(
        request=GoogleTokenSerializer,
        responses={200: GoogleTokenSerializer},
        description="Login via Google OIDC. Provide authorization code from Google frontend flow."
    )
    @action(detail=False, methods=["post"], url_path="token", permission_classes=[AllowAny])
    def login(self, request):
        code = request.data.get("code")
        redirect_uri = request.data.get("redirect_uri") or settings.GOOGLE_REDIRECT_URI

        if not code:
            return Response({"detail": "Authorization code required"}, status=status.HTTP_400_BAD_REQUEST)

        # Exchange code for tokens with Google
        data = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }

        try:
            token_resp = requests.post("https://oauth2.googleapis.com/token", data=data)
            token_resp.raise_for_status()
        except requests.RequestException as e:
            return Response({"detail": "Failed to obtain token", "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        tokens = token_resp.json()
        id_token = tokens.get("id_token")
        access_token = tokens.get("access_token")

        # Decode id_token
        decoded = jwt.decode(id_token, options={"verify_signature": False})
        email = decoded.get("email")
        first_name = decoded.get("given_name", "")
        last_name = decoded.get("family_name", "")

        # Create or update user
        user, _ = User.objects.get_or_create(email=email, defaults={
            "first_name": first_name,
            "last_name": last_name,
        })

        return Response({
            "access_token": access_token,
            "id_token": id_token,
            "expires_in": tokens.get("expires_in"),
            "token_type": tokens.get("token_type"),
            "scope": tokens.get("scope"),
        }, status=status.HTTP_200_OK)

    @extend_schema(
        request=UserSerializer,
        responses={201: UserSerializer},
        description="Register a new user locally (Google OIDC users will be created automatically on first login)"
    )
    @action(detail=False, methods=["post"], url_path="register", permission_classes=[AllowAny])
    def register(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)


@csrf_exempt
def google_callback(request):
    code = request.GET.get("code")
    if not code:
        return JsonResponse({"error": "No code provided"}, status=400)

    data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    token_resp = requests.post("https://oauth2.googleapis.com/token", data=data)
    tokens = token_resp.json()
    id_token = tokens.get("id_token")
    access_token = tokens.get("access_token")

    decoded = jwt.decode(id_token, options={"verify_signature": False})
    email = decoded.get("email")
    first_name = decoded.get("given_name", "")
    last_name = decoded.get("family_name", "")

    user, _ = User.objects.get_or_create(email=email, defaults={
        "first_name": first_name,
        "last_name": last_name,
    })

    return JsonResponse({
        "access_token": access_token,
        "id_token": id_token,
        "expires_in": tokens.get("expires_in"),
        "token_type": tokens.get("token_type"),
        "scope": tokens.get("scope"),
    })
