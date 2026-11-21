from django.conf import settings
from django.core import mail
from django.test import TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from videoflix.apps.users.models import ActivationToken, CustomUser, PasswordResetToken
from videoflix.apps.users.views import blacklist_token

PASSWORD = 'Sicheres-Passwort-123'
EMAIL = 'anna@example.com'


def create_user(email=EMAIL, verified=True):
    # Legt einen Benutzer an, optional mit bestätigter E-Mail-Adresse.
    user = CustomUser.objects.create_user(email=email, password=PASSWORD, username=email)
    user.is_email_verified = verified
    user.save()
    return user


class RegistrationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = reverse('users:register')

    def test_register_sends_email_without_exposing_token(self):
        response = self.client.post(self.url, {
            'email': EMAIL, 'password': PASSWORD, 'confirmed_password': PASSWORD,
        })

        self.assertEqual(response.status_code, 201)
        self.assertNotIn('token', response.data)
        self.assertNotIn('activation_token', response.cookies)
        self.assertEqual(len(mail.outbox), 1)
        self.assertFalse(CustomUser.objects.get(email=EMAIL).is_email_verified)

    def test_register_rejects_weak_password(self):
        response = self.client.post(self.url, {
            'email': EMAIL, 'password': '12345678', 'confirmed_password': '12345678',
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn('password', response.data)
        self.assertFalse(CustomUser.objects.filter(email=EMAIL).exists())

    def test_register_rejects_password_similar_to_email(self):
        response = self.client.post(self.url, {
            'email': EMAIL, 'password': 'anna@example', 'confirmed_password': 'anna@example',
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn('password', response.data)


class ActivationTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user(verified=False)
        self.token = ActivationToken.create_token(self.user)
        self.uidb64 = urlsafe_base64_encode(force_bytes(self.user.id))

    def activate_url(self, token):
        return reverse('users:activate', kwargs={'uidb64': self.uidb64, 'token': token})

    def test_valid_token_activates_account(self):
        response = self.client.post(self.activate_url(self.token))

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_email_verified)
        self.assertFalse(ActivationToken.objects.filter(user=self.user).exists())

    def test_activation_link_from_email_works_with_get(self):
        response = self.client.get(self.activate_url(self.token))

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_email_verified)

    def test_invalid_token_is_rejected(self):
        response = self.client.post(self.activate_url('falsch'))

        self.assertEqual(response.status_code, 400)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_email_verified)


class LoginLogoutTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.login_url = reverse('users:login')
        self.logout_url = reverse('users:logout')
        self.refresh_url = reverse('users:refresh')
        self.videos_url = '/api/videos/videos/'

    def login(self):
        response = self.client.post(self.login_url, {'email': EMAIL, 'password': PASSWORD})
        self.assertEqual(response.status_code, 200)
        return response.cookies['access_token'].value, response.cookies['refresh_token'].value

    def test_login_cookies_use_configured_secure_flag(self):
        response = self.client.post(self.login_url, {'email': EMAIL, 'password': PASSWORD})

        self.assertEqual(bool(response.cookies['access_token']['secure']), settings.AUTH_COOKIE_SECURE)

    def test_unverified_user_cannot_login(self):
        create_user(email='bob@example.com', verified=False)

        response = self.client.post(self.login_url, {'email': 'bob@example.com', 'password': PASSWORD})

        self.assertEqual(response.status_code, 400)

    def test_logout_revokes_refresh_and_access_token(self):
        access, refresh = self.login()

        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, 200)

        self.client.cookies['refresh_token'] = refresh
        self.assertEqual(self.client.post(self.refresh_url).status_code, 401)

        self.client.cookies['access_token'] = access
        self.assertEqual(self.client.get(self.videos_url).status_code, 401)

    def test_blacklisting_same_token_twice_is_harmless(self):
        _, refresh = self.login()

        blacklist_token(refresh, self.user, RefreshToken)
        blacklist_token(refresh, self.user, RefreshToken)

        self.assertEqual(self.client.post(self.refresh_url).status_code, 401)

    def test_logout_with_already_revoked_refresh_token_does_not_crash(self):
        _, refresh = self.login()
        self.client.post(self.logout_url)

        self.client.cookies['access_token'] = str(AccessToken.for_user(self.user))
        self.client.cookies['refresh_token'] = refresh
        response = self.client.post(self.logout_url)

        self.assertEqual(response.status_code, 200)


class PasswordResetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.request_url = reverse('users:password_reset_request')

    def test_request_for_unknown_email_returns_same_response(self):
        response = self.client.post(self.request_url, {'email': 'niemand@example.com'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)

    def test_reset_link_shows_form(self):
        token = PasswordResetToken.create_token(self.user)
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.id))
        url = reverse('users:password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token})

        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/html; charset=utf-8')
        self.assertContains(response, 'name="new_password"')
        self.assertContains(response, f'action="{url}"')

    def test_weak_new_password_is_rejected(self):
        token = PasswordResetToken.create_token(self.user)
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.id))
        url = reverse('users:password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token})

        response = self.client.post(url, {'new_password': '12345678', 'confirm_password': '12345678'})

        self.assertEqual(response.status_code, 400)
        self.assertIn('new_password', response.data)

    def test_valid_reset_changes_password(self):
        token = PasswordResetToken.create_token(self.user)
        uidb64 = urlsafe_base64_encode(force_bytes(self.user.id))
        url = reverse('users:password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token})
        new_password = 'Neues-Passwort-456'

        response = self.client.post(url, {'new_password': new_password, 'confirm_password': new_password})

        self.assertEqual(response.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(new_password))
