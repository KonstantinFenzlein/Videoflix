from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from videoflix.apps.users.models import TokenBlacklist

class CookieJWTAuthentication(JWTAuthentication):
    def get_validated_token(self, raw_token):
        # Validiert einen JWT-Token und gibt ihn bei Erfolg zurück.
        try:
            return super().get_validated_token(raw_token)
        except AuthenticationFailed:
            raise

    def authenticate(self, request):
        # Authentifiziert einen Benutzer anhand des Access-Tokens aus dem Cookie.
        raw_token = request.COOKIES.get('access_token')
        if not raw_token:
            return None

        try:
            validated_token = self.get_validated_token(raw_token)
            user = self.get_user(validated_token)

            if TokenBlacklist.objects.filter(token=raw_token, user=user).exists():
                raise AuthenticationFailed('Token wurde invalidiert.')

            return (user, validated_token)
        except AuthenticationFailed:
            raise AuthenticationFailed('Ungültiger oder abgelaufener Token.')
