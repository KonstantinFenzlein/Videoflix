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

- Python 3.12 (lokal) oder Docker & Docker Compose
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
- `web`: Backend API auf `http://localhost:8000/` (Entwicklung mit Reload)
- `worker`: RQ-Worker für die HLS-Konvertierung
- `db`: PostgreSQL, nur im Compose-Netz erreichbar
- `redis`: Redis für Queue und Cache, nur im Compose-Netz erreichbar

### Produktion

```bash
# .env anpassen: DEBUG=False, starkes SECRET_KEY, eigene DJANGO_SUPERUSER_*-Werte
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

- Nur nginx ist erreichbar, unter `http://localhost:8080/`. nginx liefert `/static/` aus und blockiert `/media/`. Videos, HLS und Thumbnails gibt es nur über die API.
- Der Code kommt aus dem Image, nicht aus einem Mount. Gunicorn lädt nicht neu.
- Für HTTPS davor einen TLS-Proxy betreiben und `CSRF_TRUSTED_ORIGINS` anpassen.

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

Alle Endpoints unter `/api/auth/` und `/api/videos/`. Geschützte Endpoints brauchen das Access-Token-Cookie aus dem Login.

### Authentifizierung

- `POST /api/auth/register/`: Benutzer registrieren, sendet Bestätigungs-E-Mail
- `GET` oder `POST /api/auth/activate/<uid>/<token>/`: Account aktivieren (der Link aus der E-Mail ruft per GET auf)
- `POST /api/auth/login/`: Anmelden, setzt Access- und Refresh-Cookie
- `POST /api/auth/refresh/`: Access-Token erneuern
- `POST /api/auth/logout/`: Abmelden, sperrt Access- und Refresh-Token
- `POST /api/auth/password-reset-request/`: Reset-E-Mail anfordern
- `GET /api/auth/reset-password/<uid>/<token>/`: Formular aus dem Reset-Link
- `POST /api/auth/reset-password/<uid>/<token>/`: neues Passwort setzen (`new_password`, `confirm_password`)

### Videos

- `GET /api/videos/videos/`: Liste (paginiert, Filter `?genre=<id>`)
- `GET /api/videos/videos/<id>/`: Details mit `stream_url` je Qualität
- `GET /api/videos/videos/<id>/stream/<480p|720p|1080p>/`: HLS-Playlist
- `GET /api/videos/videos/<id>/stream/<resolution>/<segment>.ts`: HLS-Segment
- `GET /api/videos/videos/<id>/thumbnail/`: Vorschaubild
- `GET /api/videos/genres/`: Alle Genres

## Environment-Variablen

Siehe `.env.template` für alle verfügbaren Einstellungen. Die Vorlage enthält Entwicklungswerte. Vor einem Produktivbetrieb müssen Passwörter und `SECRET_KEY` ersetzt werden.

## Code-Standards

- **PEP-8 Compliance**: Code folgt den PEP-8 Style Guidelines
- **Clean Code**: Funktionen ≤ 14 Zeilen, Single Responsibility Principle
- **Dokumentation**: Kommentare an Funktionen und README für alle Features

## Tests

```bash
python manage.py test
# im Container:
docker compose exec web python manage.py test
```

## Lizenz

Dieses Projekt ist Teil der Developer Akademie.
