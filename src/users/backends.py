from mozilla_django_oidc.auth import OIDCAuthenticationBackend


class MyOIDCBackend(OIDCAuthenticationBackend):
    def create_user(self, claims):
        email = claims.get("email")
        if not email:
            raise ValueError("OIDC provider did not return an email.")
        user = super().create_user(claims)
        self._update_fields_from_claims(user, claims)
        return user

    def update_user(self, user, claims):
        self._update_fields_from_claims(user, claims)
        return user

    def _update_fields_from_claims(self, user, claims):
        user.email = claims.get("email", user.email)
        user.first_name = claims.get("given_name", user.first_name)
        user.last_name = claims.get("family_name", user.last_name)
        user.save()
