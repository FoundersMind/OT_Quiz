# create_superuser.py
from django.contrib.auth import get_user_model

User = get_user_model()

username = "naman"
password = "naman"

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email="", password=password)
    print("Superuser 'naman' created.")
else:
    print("Superuser 'naman' already exists.")
