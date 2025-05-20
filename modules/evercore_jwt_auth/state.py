from .settings import jwt_auth_settings
from .backends import EvercoreJWTBackend

token_backend = EvercoreJWTBackend(
    jwt_auth_settings.ALGORITHM,
    jwt_auth_settings.SIGNING_KEY,
    jwt_auth_settings.VERIFYING_KEY,
    jwt_auth_settings.AUDIENCE,
    jwt_auth_settings.ISSUER,
    jwt_auth_settings.JWK_URL,
    jwt_auth_settings.LEEWAY,
    jwt_auth_settings.JSON_ENCODER,
)
