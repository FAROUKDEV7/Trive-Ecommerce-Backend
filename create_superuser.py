# create_superuser.py
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "trive_backend.settings")
django.setup()

from apps.users.models import User

email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
first_name = "Admin"
last_name = "User"

# لو مستخدم بالفعل
if not User.objects.filter(email=email).exists():
    User.objects.create_superuser(
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name
    )
    print(f"Superuser {email} created.")
else:
    print(f"Superuser {email} already exists.")