import os
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.db import transaction

try:
    from django.contrib.sites.models import Site
except Exception:  # pragma: no cover
    Site = None

from reservas.models import Cancha


class Command(BaseCommand):
    help = (
        "Run migrations, create a superuser from env vars if missing, "
        "configure Sites domain, and seed initial data."
    )

    def handle(self, *args, **options):
        # 1) Ensure DB schema is up to date
        self.stdout.write(self.style.NOTICE("Applying migrations..."))
        call_command("migrate", interactive=False)

        # 2) Create superuser from env vars if provided
        self._ensure_superuser()

        # 3) Configure Sites domain if available
        self._configure_site_domain()

        # 4) Seed minimal data
        self._seed_initial_canchas()

        self.stdout.write(self.style.SUCCESS("Bootstrap completed."))

    def _ensure_superuser(self):
        User = get_user_model()
        username = os.getenv("DJANGO_SUPERUSER_USERNAME")
        email = os.getenv("DJANGO_SUPERUSER_EMAIL")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD")

        if not (username and email and password):
            self.stdout.write(
                self.style.WARNING(
                    "Superuser env vars not fully provided; skipping superuser creation."
                )
            )
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.SUCCESS(f"Superuser '{username}' already exists."))
            return

        self.stdout.write(self.style.NOTICE(f"Creating superuser '{username}'..."))
        with transaction.atomic():
            User.objects.create_superuser(username=username, email=email, password=password)
        self.stdout.write(self.style.SUCCESS("Superuser created."))

    def _configure_site_domain(self):
        if Site is None:
            self.stdout.write(self.style.WARNING("django.contrib.sites not installed; skipping Sites configuration."))
            return

        # Prefer explicit APP_DOMAIN; fallback to RENDER_EXTERNAL_URL or ALLOWED_HOSTS[0]
        app_domain = os.getenv("APP_DOMAIN")
        render_url = os.getenv("RENDER_EXTERNAL_URL")  # e.g., https://yourapp.onrender.com
        allowed_hosts = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "").split(",") if h.strip()]

        domain = None
        if app_domain:
            domain = app_domain
        elif render_url:
            # Strip scheme from render URL for Sites.domain
            domain = render_url.replace("https://", "").replace("http://", "").strip("/")
        elif allowed_hosts:
            domain = allowed_hosts[0]

        if not domain:
            self.stdout.write(self.style.WARNING("No domain found in env; skipping Sites domain update."))
            return

        site = Site.objects.get_current()
        site.domain = domain
        site.name = os.getenv("SITE_NAME", "Turnero Padel")
        site.save(update_fields=["domain", "name"])
        self.stdout.write(self.style.SUCCESS(f"Sites configured: domain='{site.domain}', name='{site.name}'"))

    def _seed_initial_canchas(self):
        if Cancha.objects.exists():
            self.stdout.write(self.style.SUCCESS("Canchas already present; skipping seed."))
            return
        Cancha.objects.get_or_create(nombre="Cancha 1", activa=True)
        Cancha.objects.get_or_create(nombre="Cancha 2", activa=True)
        self.stdout.write(self.style.SUCCESS("Seeded initial Canchas: Cancha 1, Cancha 2"))
