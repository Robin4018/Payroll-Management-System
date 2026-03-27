from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.http import HttpResponse

def auto_login(request):
    username = request.GET.get('user')
    if not username:
        return HttpResponse("Username required", status=400)
    try:
        user = User.objects.get(username=username)
        # Manually specify the backend to avoid MultipleBackendError
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        next_url = request.GET.get('next', '/dashboard/college/')
        return redirect(next_url)
    except User.DoesNotExist:
        return HttpResponse(f"User {username} not found", status=404)
