from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import EmailValidator
import secrets
from datetime import timedelta
from django.utils import timezone

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    is_email_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'custom_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.email

class ActivationToken(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='activation_token')
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = 'activation_token'
        verbose_name = 'Activation Token'
        verbose_name_plural = 'Activation Tokens'

    def is_valid(self):
        # Prüft, ob der Aktivierungstoken noch gültig ist.
        return timezone.now() < self.expires_at

    @classmethod
    def create_token(cls, user):
        # Erstellt oder aktualisiert einen neuen Aktivierungstoken für einen Benutzer.
        token = secrets.token_urlsafe(32)
        expires_at = timezone.now() + timedelta(hours=24)
        activation_token, _ = cls.objects.update_or_create(
            user=user,
            defaults={'token': token, 'expires_at': expires_at}
        )
        return token

    def __str__(self):
        return f"Token for {self.user.email}"

class TokenBlacklist(models.Model):
    token = models.TextField(unique=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='blacklisted_tokens')
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        db_table = 'token_blacklist'
        verbose_name = 'Token Blacklist'
        verbose_name_plural = 'Token Blacklists'
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['expires_at']),
        ]

    def __str__(self):
        return f"Blacklisted token for {self.user.email}"
