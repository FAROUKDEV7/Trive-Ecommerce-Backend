import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "trive_backend.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@gmail.com")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD", "12345678")

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print("Superuser created successfully!")
else:
    u = User.objects.get(username=username)
    u.set_password(password)
    u.save()
    print("Superuser already exists. Password updated!")