from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Create or reset a superuser"

    def handle(self, *args, **options):
        User = get_user_model()
        username = "admin"
        email = "admin@example.com"
        password = "ChangeThisPassword123!"

        user, created = User.objects.get_or_create(username=username)
        user.email = email
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS("Superuser created"))
        else:
            self.stdout.write(self.style.SUCCESS("Superuser password reset"))
