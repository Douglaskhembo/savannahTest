import os
from drf_spectacular.extensions import OpenApiAuthenticationExtension


class OIDCAuthenticationScheme(OpenApiAuthenticationExtension):
    target_class = "src.config.authentication.GoogleOIDCAuthentication"
    name = "oauth2"

    def get_security_definition(self, auto_schema):
        return {
            "type": "oauth2",
            "flows": {
                "authorizationCode": {
                    "authorizationUrl": os.getenv("OIDC_OP_AUTHORIZATION_ENDPOINT",
                                                  "https://accounts.google.com/o/oauth2/v2/auth"),
                    "tokenUrl": os.getenv("OIDC_OP_TOKEN_ENDPOINT", "https://oauth2.googleapis.com/token"),
                    "scopes": {
                        "openid": "OpenID Connect scope",
                        "email": "Access to email",
                        "profile": "Access to profile",
                    },
                }
            },
        }
