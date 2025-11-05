from rest_framework import authentication, exceptions
import requests


class GoogleOIDCAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return None

        token = auth.split(" ", 1)[1].strip()
        if not token:
            return None

        # Automatic userinfo authentication
        userinfo_url = "https://openidconnect.googleapis.com/v1/userinfo"
        try:
            resp = requests.get(userinfo_url, headers={"Authorization": f"Bearer {token}"}, timeout=5)
        except requests.RequestException:
            raise exceptions.AuthenticationFailed("Failed to validate token with provider")

        if resp.status_code != 200:
            raise exceptions.AuthenticationFailed("Invalid or expired access token")

        user_info = resp.json()
        email = user_info.get("email")
        if not email:
            raise exceptions.AuthenticationFailed("No email in token")

        from django.contrib.auth import get_user_model
        User = get_user_model()
        user, _ = User.objects.get_or_create(email=email, defaults={
            "first_name": user_info.get("given_name", ""),
            "last_name": user_info.get("family_name", ""),
        })

        return (user, None)
