import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pos_final.settings')
django.setup()

from django.contrib.auth.models import User
from pos_app.models import UserProfile

password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin1234')

user, created = User.objects.get_or_create(username='admin')
if created:
    user.set_password(password)
    user.is_superuser = True
    user.is_staff = True
    user.save()
    print("Admin user created!")
else:
    print("Admin user already exists, skipping creation.")

profile, _ = UserProfile.objects.update_or_create(
    user=user,
    defaults={'role': 'admin'}
)
print(f"Admin profile role set to: {profile.role}")