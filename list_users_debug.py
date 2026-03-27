from django.contrib.auth.models import User
print("Users count:", User.objects.count())
for u in User.objects.all():
    print(f"User: {u.username}, Super: {u.is_superuser}, Staff: {u.is_staff}")
