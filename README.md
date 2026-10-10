# Videoflix - Backend

Ein Django REST Framework Backend für eine Video-Streaming-Plattform mit Authentifizierung, Videoausgabe in HLS-Format und Background-Task-Verarbeitung.

## Features

- **Benutzerregistrierung & Authentifizierung**: Email-Verifikation, Login/Logout, Passwort-Reset
- **Video-Management**: Verwaltung von Videos mit Multiple Quality Levels (480p, 720p, 1080p)
- **HLS-Streaming**: Automatische Konvertierung zu HLS-Format mit FFmpeg
- **Background Tasks**: Django-RQ für Video-Konvertierung und Email-Versand
- **Caching Layer**: Redis für Performance-Optimierung
- **REST API**: Django REST Framework mit Token-Authentication
- **Docker**: Vollständige Docker-Konfiguration

## Voraussetzungen

- Python 3.11+ (lokal) oder Docker & Docker Compose
- PostgreSQL 15+ (lokal)
- Redis 7+ (lokal)
- FFmpeg

## Installation

### Mit Docker (empfohlen)

```bash
cp .env.template .env
docker-compose up --build
```

**Admin-Zugang:**
- URL: `http://localhost:8000/admin/`
- Username: `admin` (aus .env: DJANGO_SUPERUSER_USERNAME)
- Password: (aus .env: DJANGO_SUPERUSER_PASSWORD)

**Services:**
- Backend API: `http://localhost:8000/`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`

### Lokal (Entwicklung)

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.template .env

# PostgreSQL & Redis starten (Optional: mit Docker)
docker run -d --name videoflix_db -e POSTGRES_PASSWORD=videoflixpassword -e POSTGRES_DB=videoflix -p 5432:5432 postgres:latest
docker run -d --name videoflix_redis -p 6379:6379 redis:latest

# Migrationen & Admin erstellen
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Projektstruktur

```
videoflix/
├── config/              # Django-Konfiguration
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── apps/
│   ├── users/          # Benutzer-App
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   └── urls.py
│   └── videos/         # Video-App
│       ├── models.py
│       ├── views.py
│       ├── serializers.py
│       └── urls.py
├── utils/
│   ├── email.py        # Email-Funktionen
│   └── video.py        # Video-Verarbeitung
├── static/             # Statische Dateien
├── media/              # Hochgeladene Dateien
│   ├── videos/
│   └── thumbnails/
├── templates/          # Email-Templates
└── manage.py
```

## API-Endpoints

### Authentifizierung

- `POST /api/auth/register/` - Benutzer registrieren
- `POST /api/auth/login/` - Anmelden
- `POST /api/auth/logout/` - Abmelden

### Videos

- `GET /api/videos/videos/` - Alle Videos auflisten
- `GET /api/videos/videos/{id}/` - Video-Details
- `GET /api/videos/genres/` - Alle Genres

## Environment-Variablen

Siehe `.env.example` für alle verfügbaren Einstellungen.

## Code-Standards

- **PEP-8 Compliance**: Code folgt den PEP-8 Style Guidelines
- **Clean Code**: Funktionen ≤ 14 Zeilen, Single Responsibility Principle
- **Dokumentation**: Docstrings und README für alle Features

## Tests

```bash
python manage.py test
```

## Lizenz

Dieses Projekt ist Teil der Developer Akademie.
