from rest_framework import serializers
from .models import CustomUser, ActivationToken

class UserRegistrationSerializer(serializers.ModelSerializer):
    # Validiert und erstellt einen neuen Benutzer mit E-Mail und Passwort.
    password = serializers.CharField(write_only=True, min_length=8)
    confirmed_password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = CustomUser
        fields = ('email', 'password', 'confirmed_password')

    def validate_email(self, value):
        # Prüft, ob die E-Mail bereits registriert ist.
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError('Bitte überprüfe deine Eingaben und versuche es erneut.')
        return value

    def validate(self, data):
        # Prüft, ob die Passwörter übereinstimmen.
        if data['password'] != data['confirmed_password']:
            raise serializers.ValidationError('Bitte überprüfe deine Eingaben und versuche es erneut.')
        return data

    def create(self, validated_data):
        # Erstellt einen neuen Benutzer mit den validierten Daten.
        validated_data.pop('confirmed_password')
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            username=validated_data['email']
        )
        return user

class UserLoginSerializer(serializers.Serializer):
    # Validiert Anmeldedaten mit E-Mail und Passwort.
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class UserDetailSerializer(serializers.ModelSerializer):
    # Gibt Benutzerdetails mit Verifizierungsstatus zurück.
    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'first_name', 'last_name', 'is_email_verified')
        read_only_fields = ('id', 'is_email_verified')
