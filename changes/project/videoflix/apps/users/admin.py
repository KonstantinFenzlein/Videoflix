from django.contrib import admin
from .models import CustomUser, ActivationToken, TokenBlacklist, PasswordResetToken

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    # Konfiguriert die Admin-Oberfläche für Benutzerverwaltung mit Filterung und Suche.
    list_display = ('email', 'first_name', 'last_name', 'is_email_verified', 'created_at')
    list_filter = ('is_email_verified', 'created_at')
    search_fields = ('email', 'first_name', 'last_name')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(ActivationToken)
class ActivationTokenAdmin(admin.ModelAdmin):
    # Konfiguriert die Admin-Oberfläche für Aktivierungstoken-Verwaltung.
    list_display = ('user', 'is_valid', 'created_at', 'expires_at')
    list_filter = ('created_at', 'expires_at')
    search_fields = ('user__email',)
    readonly_fields = ('token', 'created_at')

@admin.register(PasswordResetToken)
class PasswordResetTokenAdmin(admin.ModelAdmin):
    # Konfiguriert die Admin-Oberfläche für Passwort-Reset-Token-Verwaltung.
    list_display = ('user', 'is_valid', 'created_at', 'expires_at')
    list_filter = ('created_at', 'expires_at')
    search_fields = ('user__email',)
    readonly_fields = ('token', 'created_at')

@admin.register(TokenBlacklist)
class TokenBlacklistAdmin(admin.ModelAdmin):
    # Konfiguriert die Admin-Oberfläche für die Verwaltung ungültiger Refresh-Tokens.
    list_display = ('user', 'created_at', 'expires_at')
    list_filter = ('created_at', 'expires_at')
    search_fields = ('user__email',)
    readonly_fields = ('token', 'created_at')
