from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.exceptions import PermissionDenied
from drf_spectacular.utils import extend_schema
from django.conf import settings
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse
import requests
import jwt

from .serializers import UserSerializer
from .permissions import IsOwnerOrAdmin

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ["register", "token"]:
            return [AllowAny()]
        elif self.action == "list":
            return [IsAdminUser()]
        elif self.action in ["retrieve", "update", "partial_update", "destroy"]:
            return [IsOwnerOrAdmin()]
        return super().get_permissions()

    def perform_destroy(self, instance):
        request = self.request
        if request.user.role == User.Role.ADMIN:
            instance.delete()
        elif instance == request.user:
            instance.is_active = False
            instance.save()
        else:
            raise PermissionDenied("You can only delete your own account.")

    @extend_schema(
        description="Exchange Google authorization code for access_token and id_token. "
                    "Use the returned access_token in Swagger Authorize → Bearer <token>.",
        request=None,
        responses={200: dict},
    )
    @action(detail=False, methods=["post"], url_path="token", permission_classes=[AllowAny])
    def token(self, request):
        code = request.data.get("code")
        redirect_uri = request.data.get("redirect_uri") or settings.GOOGLE_REDIRECT_URI

        if not code:
            return Response({"detail": "Authorization code required"}, status=status.HTTP_400_BAD_REQUEST)

        data = {
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": redirect_uri,
            "grant_type": "authorization_code",
        }

        try:
            token_resp = requests.post("https://oauth2.googleapis.com/token", data=data, timeout=10)
            token_resp.raise_for_status()
        except requests.RequestException as e:
            return Response({"detail": "Failed to obtain token", "error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        tokens = token_resp.json()
        id_token = tokens.get("id_token")
        access_token = tokens.get("access_token")

        if not id_token or not access_token:
            return Response({"detail": "Missing id_token or access_token"}, status=status.HTTP_400_BAD_REQUEST)

        decoded = jwt.decode(id_token, options={"verify_signature": False})
        email = decoded.get("email")
        first_name = decoded.get("given_name", "")
        last_name = decoded.get("family_name", "")

        if not email:
            return Response({"detail": "No email returned by provider"}, status=status.HTTP_400_BAD_REQUEST)

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
        description="Register a new user locally. OIDC users are created automatically on first login via Google.",
        request=UserSerializer,
        responses={201: UserSerializer},
    )
    @action(detail=False, methods=["post"], url_path="register", permission_classes=[AllowAny])
    def register(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

    @extend_schema(
        description="Get or update the logged-in user without needing their ID."
    )
    @action(detail=False, methods=["get", "put", "patch"], url_path="me", permission_classes=[IsOwnerOrAdmin])
    def me(self, request):
        user = request.user
        if request.method in ["PUT", "PATCH"]:
            serializer = self.get_serializer(user, data=request.data, partial=(request.method == "PATCH"))
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        return Response(self.get_serializer(user).data)


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

    try:
        token_resp = requests.post("https://oauth2.googleapis.com/token", data=data, timeout=10)
        token_resp.raise_for_status()
    except requests.RequestException as e:
        return JsonResponse({"error": "Failed to obtain token", "details": str(e)}, status=400)

    tokens = token_resp.json()
    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")
    id_token = tokens.get("id_token")

    if not access_token or not id_token:
        return JsonResponse({"error": "Missing id_token or access_token"}, status=400)

    html = f"""
    <html>
    <body style="font-family: sans-serif; padding: 2rem;">
        <h2>Google OAuth Tokens</h2>
        <p><b>Access Token:</b> <code>{access_token}</code></p>
        <p><b>Refresh Token:</b> <code>{refresh_token}</code></p>
        <p><b>ID Token:</b> <code>{id_token}</code></p>
        <p>Use the <b>Access Token</b> in Swagger Authorize → Bearer &lt;token&gt;</p>
    </body>
    </html>
    """
    return HttpResponse(html)
