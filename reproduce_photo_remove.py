import os
import django
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.conf import settings
settings.ALLOWED_HOSTS += ['testserver']

from rest_framework.test import APIRequestFactory, force_authenticate
from employees.views import EmployeeViewSet
from employees.models import Employee
from tenants.models import Tenant
from django.contrib.auth.models import User

def test_photo_remove():
    print("Setting up test data...")
    tenant, _ = Tenant.objects.get_or_create(name="Test Photo Tenant")
    
    # Ensure fresh user
    if User.objects.filter(username="test_remove_user").exists():
        user = User.objects.get(username="test_remove_user")
        # Ensure no employee attached to avoid OneToOne issue
        if hasattr(user, 'employee'):
             user.employee.delete()
    else:
        user = User.objects.create(username="test_remove_user")
    
    # Create employee with a photo first
    image_file = BytesIO()
    image = Image.new('RGB', (100, 100), 'blue')
    image.save(image_file, 'JPEG')
    image_file.seek(0)
    file = SimpleUploadedFile("profile_to_remove.jpg", image_file.getvalue(), content_type="image/jpeg")

    employee, _ = Employee.objects.get_or_create(
        employee_code="PHOTO_REM_001",
        defaults={
            'first_name': "Remove",
            'last_name': "Photo",
            'email': "remove@test.com",
            'tenant': tenant,
            'user': user,
            'date_of_joining': "2023-01-01"
        }
    )
    # Manually set photo
    employee.profile_photo = file
    employee.save()
    employee.refresh_from_db()
    print(f"Initial photo: {employee.profile_photo}")

    # Create Request to Remove (SET TO NULL)
    factory = APIRequestFactory()
    url = f'/api/employees/{employee.id}/'
    
    # Try sending JSON with null
    data = {'profile_photo': None}
    request = factory.patch(url, data, format='json')
    force_authenticate(request, user=user)
    
    view = EmployeeViewSet.as_view({'patch': 'partial_update'})
    response = view(request, pk=employee.id)
    
    with open("debug_remove.txt", "a") as f:
        f.write(f"Response Status: {response.status_code}\n")
        # f.write(f"Response Data: {response.data}\n") # Can be large
        
        employee.refresh_from_db()
        if not employee.profile_photo:
            print("Success! Photo removed.")
            f.write("Success! Photo removed.\n")
        else:
            print(f"Failed. Photo still exists: {employee.profile_photo}")
            f.write(f"Failed. Photo still exists: {employee.profile_photo}\n")

if __name__ == "__main__":
    with open("debug_remove.txt", "w") as f:
        f.write("Starting...\n")
    try:
        test_photo_remove()
    except Exception as e:
        print(f"Error: {e}")
        with open("debug_remove.txt", "a") as f:
            f.write(f"Error: {e}\n")
