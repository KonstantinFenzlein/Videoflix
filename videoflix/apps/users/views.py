from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST, HTTP_200_OK, HTTP_401_UNAUTHORIZED
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_str, force_bytes
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from django.utils import timezone
from datetime import datetime
from .serializers import UserRegistrationSerializer, UserLoginSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer
from .models import ActivationToken, CustomUser, TokenBlacklist, PasswordResetToken
from videoflix.utils.email import send_verification_email, send_password_reset_email

class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Registriert einen neuen Benutzer und sendet eine E-Mail-Verifizierung.
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            token = ActivationToken.create_token(user)
            uidb64 = urlsafe_base64_encode(force_bytes(user.id))
            activation_link = f"{request.build_absolute_uri('/api/auth/activate')}/{uidb64}/{token}/"
            send_verification_email(user, activation_link)

            response_data = {
                'user': {'id': user.id, 'email': user.email},
                'token': token
            }
            response = Response(response_data, status=HTTP_201_CREATED)
            response.set_cookie('activation_token', token, httponly=True, secure=False, samesite='Lax')
            return response
        return Response({'error': 'Bitte überprüfe deine Eingaben und versuche es erneut.'}, status=HTTP_400_BAD_REQUEST)

class ActivateUserView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        # Aktiviert einen Benutzernaccount durch Verifizierung des Aktivierungstokens.
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(id=user_id)
        except (CustomUser.DoesNotExist, ValueError):
            return Response({'error': 'Ungültige Benutzer-ID.'}, status=HTTP_400_BAD_REQUEST)

        try:
            activation_token = ActivationToken.objects.get(user=user, token=token)
            if not activation_token.is_valid():
                return Response({'error': 'Token abgelaufen.'}, status=HTTP_400_BAD_REQUEST)

            user.is_email_verified = True
            user.is_active = True
            user.save()
            activation_token.delete()
            return Response({'message': 'Account successfully activated.'}, status=HTTP_200_OK)
        except ActivationToken.DoesNotExist:
            return Response({'error': 'Ungültiger Token.'}, status=HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Authentifiziert einen Benutzer und gibt Access- und Refresh-Tokens aus.
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']

            user = authenticate(request, username=email, password=password)
            if user is None:
                return Response(
                    {'error': 'Bitte überprüfe deine Eingaben und versuche es erneut.'},
                    status=HTTP_400_BAD_REQUEST
                )

            if not user.is_email_verified:
                return Response(
                    {'error': 'Bitte überprüfe deine Eingaben und versuche es erneut.'},
                    status=HTTP_400_BAD_REQUEST
                )

            refresh = RefreshToken.for_user(user)
            response_data = {
                'detail': 'Login successful',
                'user': {'id': user.id, 'username': user.email}
            }
            response = Response(response_data, status=HTTP_200_OK)
            response.set_cookie(
                'access_token',
                str(refresh.access_token),
                httponly=True,
                secure=False,
                samesite='Lax',
                max_age=15*60
            )
            response.set_cookie(
                'refresh_token',
                str(refresh),
                httponly=True,
                secure=False,
                samesite='Lax',
                max_age=7*24*60*60
            )
            return response
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Erneuert den Access-Token mit Hilfe eines gültigen Refresh-Tokens.
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response(
                {'detail': 'Refresh-Token fehlt.'},
                status=HTTP_400_BAD_REQUEST
            )

        if TokenBlacklist.objects.filter(token=refresh_token).exists():
            return Response(
                {'detail': 'Ungültiger Refresh-Token.'},
                status=HTTP_401_UNAUTHORIZED
            )

        try:
            refresh = RefreshToken(refresh_token)
            response_data = {
                'detail': 'Token refreshed',
                'access': str(refresh.access_token)
            }
            response = Response(response_data, status=HTTP_200_OK)
            response.set_cookie(
                'access_token',
                str(refresh.access_token),
                httponly=True,
                secure=False,
                samesite='Lax',
                max_age=15*60
            )
            return response
        except Exception as e:
            return Response(
                {'detail': 'Ungültiger Refresh-Token.'},
                status=HTTP_401_UNAUTHORIZED
            )

class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Sendet einen Passwort-Reset-Link an die E-Mail des Benutzers.
        serializer = PasswordResetRequestSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = CustomUser.objects.get(email=email)
                token = PasswordResetToken.create_token(user)
                uidb64 = urlsafe_base64_encode(force_bytes(user.id))
                reset_link = f"{request.build_absolute_uri('/api/auth/reset-password')}/{uidb64}/{token}/"
                send_password_reset_email(user, reset_link)
            except CustomUser.DoesNotExist:
                pass

            return Response(
                {'detail': 'An email has been sent to reset your password.'},
                status=HTTP_200_OK
            )
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        # Bestätigt die Passwortänderung mit dem Token aus der E-Mail.
        serializer = PasswordResetConfirmSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = CustomUser.objects.get(id=user_id)
        except (CustomUser.DoesNotExist, ValueError):
            return Response({'error': 'Ungültiger Benutzer.'}, status=HTTP_400_BAD_REQUEST)

        try:
            password_reset_token = PasswordResetToken.objects.get(user=user, token=token)
            if not password_reset_token.is_valid():
                return Response({'error': 'Token abgelaufen.'}, status=HTTP_400_BAD_REQUEST)

            user.set_password(serializer.validated_data['new_password'])
            user.save()
            password_reset_token.delete()

            return Response(
                {'detail': 'Your Password has been successfully reset.'},
                status=HTTP_200_OK
            )
        except PasswordResetToken.DoesNotExist:
            return Response({'error': 'Ungültiger Token.'}, status=HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Meldet einen Benutzer ab und setzt seinen Refresh-Token auf die Blacklist.
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response(
                {'detail': 'Refresh-Token fehlt.'},
                status=HTTP_400_BAD_REQUEST
            )

        try:
            refresh = RefreshToken(refresh_token)
            expires_at = datetime.fromtimestamp(refresh['exp'], tz=timezone.utc)
            TokenBlacklist.objects.create(
                token=refresh_token,
                user=request.user,
                expires_at=expires_at
            )
        except TokenError:
            return Response(
                {'detail': 'Ungültiger oder abgelaufener Refresh Token.'},
                status=HTTP_400_BAD_REQUEST
            )

        response_data = {
            'detail': 'Logout successful! All tokens will be deleted. Refresh token is now invalid.'
        }
        response = Response(response_data, status=HTTP_200_OK)
        response.delete_cookie('access_token')
        response.delete_cookie('refresh_token')
        return response
