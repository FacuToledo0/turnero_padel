# Turnero Pádel – Despliegue a Producción

Este proyecto es una app Django para gestionar reservas de canchas de pádel. Está preparada para desplegarse en proveedores PaaS como Render o Railway con PostgreSQL gestionado, estáticos servidos con WhiteNoise y Gunicorn como servidor WSGI.

## Requisitos
- Python 3.11+ recomendado
- Cuenta en Render (o Railway)
- Repo en Git (idealmente GitHub/GitLab)

## Variables de entorno
Copia `.env.example` a `.env` para desarrollo local y completa:

- `SECRET_KEY`: Clave segura de Django (usa algo fuerte en producción)
- `DEBUG`: `False` en producción
- `ALLOWED_HOSTS`: dominios permitidos separados por coma
- `CSRF_TRUSTED_ORIGINS`: orígenes HTTPS confiables separados por coma (ej.: `https://tuapp.onrender.com`)
- `DATABASE_URL`: cadena de conexión de Postgres (el proveedor la inyecta automáticamente)
- `DB_SSL_REQUIRED`: `True` en producción
- `DB_CONN_MAX_AGE`: `600` por defecto

## Instalación local
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # edita DEBUG=True en local
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
python manage.py runserver
```

## Estructura clave
- `turnero_padel/settings.py`: usa variables de entorno, WhiteNoise y `dj-database-url` con fallback a SQLite.
- `Procfile`: ejecuta la app con `gunicorn turnero_padel.wsgi:application`.
- `render.yaml`: manifiesto para desplegar en Render (servicio web + base de datos Postgres).

## Despliegue en Render
1. Crea un nuevo repo y sube el proyecto.
2. En Render, crea un nuevo servicio Web desde el repo.
3. Deja que Render detecte el proyecto Python o usa `render.yaml` desde el repo.
4. Configura env vars:
   - `SECRET_KEY`: valor seguro
   - `DEBUG=False`
   - `ALLOWED_HOSTS`: `tu-servicio.onrender.com`
   - `CSRF_TRUSTED_ORIGINS`: `https://tu-servicio.onrender.com`
   - `DATABASE_URL`: se inyecta automáticamente si creas la DB en Render (está en `render.yaml`).
5. Render ejecutará:
   - `pip install -r requirements.txt`
   - `python manage.py collectstatic --noinput`
   - `gunicorn turnero_padel.wsgi:application --log-file -`
6. Tras el primer deploy, ejecuta en Shell de Render o desde CI/CD:
```bash
python manage.py migrate
python manage.py createsuperuser
```

## Migración de datos
Actualmente el proyecto usa SQLite (`db.sqlite3`). Para mover datos a Postgres:
- Opción simple: empezar limpio en producción.
- Opción con exportación: `python manage.py dumpdata > backup.json` y luego en Postgres `python manage.py loaddata backup.json` (cuidar usuarios/contraseñas y tablas con claves únicas).

## Static files
- `STATIC_ROOT` apunta a `staticfiles/`. En el build de Render se ejecuta `collectstatic`.
- WhiteNoise sirve los estáticos en producción.

## Notas
- `ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS` deben incluir tu dominio final.
- Si usas dominio propio, configura CNAME a la URL del servicio y actualiza `ALLOWED_HOSTS`/`CSRF_TRUSTED_ORIGINS`.

## Soporte
Si necesitas que automatice la creación del servicio en Render o Railway, compárteme el repositorio remoto y el dominio deseado, y te ayudo a completar el proceso.
