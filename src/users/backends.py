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
        user.phone = claims.get("phone_number", user.phone)

        # 🔑 Role mapping from Auth0 claim
        roles_claim = claims.get("https://savannah-api/roles", [])
        if roles_claim:
            # Pick the first role (or extend to support multiple)
            role = roles_claim[0].upper()
            if role in dict(user.Role.choices):
                user.role = role

        user.save()
