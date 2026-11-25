from django.core.mail import send_mail
from django.template.loader import render_to_string

def send_verification_email(user, activation_link):
    # Sendet eine E-Mail-Verifizierungsnachricht an den Benutzer.
    context = {'user': user, 'activation_link': activation_link}
    html_message = render_to_string('emails/verification.html', context)
    send_mail(
        'Bestätige deine E-Mail Adresse',
        'Bitte bestätige deine E-Mail Adresse',
        None,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )

def send_password_reset_email(user, reset_link):
    # Sendet eine Passwort-Zurücksetzen-E-Mail an den Benutzer.
    context = {'user': user, 'reset_link': reset_link}
    html_message = render_to_string('emails/password_reset.html', context)
    send_mail(
        'Passwort zurücksetzen',
        'Setze dein Passwort zurück',
        None,
        [user.email],
        html_message=html_message,
        fail_silently=False,
    )
