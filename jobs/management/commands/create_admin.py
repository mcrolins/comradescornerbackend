import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Create or reset an admin user from env vars"

    def handle(self, *args, **options):
        User = get_user_model()

        username = os.getenv("ADMIN_USERNAME", "mcrolins")
        email = os.getenv("ADMIN_EMAIL", "rolinsmac21@gmail.com")
        password = os.getenv("ADMIN_PASSWORD")

        if not password:
            self.stdout.write(self.style.WARNING("ADMIN_PASSWORD not set; skipping superuser creation"))
            return

        user, created = User.objects.get_or_create(username=username)
        user.email = email
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        self.stdout.write(self.style.SUCCESS("Superuser created" if created else "Superuser password reset"))

