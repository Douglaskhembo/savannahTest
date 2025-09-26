import os
from drf_spectacular.extensions import OpenApiAuthenticationExtension

class OIDCAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = "mozilla_django_oidc.contrib.drf.OIDCAuthentication"
    name = "openid"

    def get_security_definition(self, auto_schema):
        return {
            "type": "oauth2",
            "flows": {
                "authorizationCode": {
                    "authorizationUrl": os.getenv("OIDC_OP_AUTHORIZATION_ENDPOINT"),
                    "tokenUrl": os.getenv("OIDC_OP_TOKEN_ENDPOINT"),
                    "scopes": {
                        "openid": "OpenID Connect scope",
                        "email": "Access to email",
                        "profile": "Access to profile",
                    },
                }
            },
        }
