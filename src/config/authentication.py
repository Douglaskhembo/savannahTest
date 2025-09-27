from rest_framework import authentication, exceptions
import requests


class GoogleOIDCAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return None

        token = auth.split(" ")[1]
        # Validate with Google
        resp = requests.get(f"https://www.googleapis.com/oauth2/v3/tokeninfo?id_token={token}")
        if resp.status_code != 200:
            raise exceptions.AuthenticationFailed("Invalid Google token")

        user_info = resp.json()
        email = user_info.get("email")
        if not email:
            raise exceptions.AuthenticationFailed("No email in token")

        # Get or create local user
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user, _ = User.objects.get_or_create(email=email)
        return (user, None)
