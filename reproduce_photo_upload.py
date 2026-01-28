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

def test_photo_upload():
    print("Setting up test data...")
    # 1. Create Tenant & User
    tenant, _ = Tenant.objects.get_or_create(name="Test Photo Tenant")
    user, _ = User.objects.get_or_create(username="test_photo_user")
    
    # 2. Create Employee
    employee, created = Employee.objects.get_or_create(
        employee_code="PHOTO001",
        defaults={
            'first_name': "Photo",
            'last_name': "Tester",
            'email': "photo@test.com",
            'tenant': tenant,
            'user': user,
            'date_of_joining': "2023-01-01"
        }
    )
    
    # 3. Create Dummy Image
    image_file = BytesIO()
    image = Image.new('RGB', (100, 100), 'red')
    image.save(image_file, 'JPEG')
    image_file.seek(0)
    
    file = SimpleUploadedFile("profile.jpg", image_file.getvalue(), content_type="image/jpeg")
    
    # 4. Create Request
    factory = APIRequestFactory()
    url = f'/api/employees/{employee.id}/'
    data = {'profile_photo': file}
    request = factory.patch(url, data, format='multipart')
    force_authenticate(request, user=user)
    
    # 5. Process View
    view = EmployeeViewSet.as_view({'patch': 'partial_update'})
    response = view(request, pk=employee.id)
    
    with open("photo_upload_result.txt", "w") as f:
        print(f"Response Status: {response.status_code}")
        f.write(f"Response Status: {response.status_code}\n")
        if response.status_code in [200, 204]:
            employee.refresh_from_db()
            if employee.profile_photo:
                print(f"Success! Photo uploaded to: {employee.profile_photo.url}")
                f.write(f"Success! Photo uploaded to: {employee.profile_photo.url}\n")
            else:
                print("Response OK but photo not set on model.")
                f.write("Response OK but photo not set on model.\n")
        else:
            print(f"Failed: {response.data}")
            f.write(f"Failed: {response.data}\n")

if __name__ == "__main__":
    with open("debug_photo.txt", "w") as f:
        f.write("Starting script...\n")
    try:
        test_photo_upload()
        with open("debug_photo.txt", "a") as f:
            f.write("Script finished successfully.\n")
    except Exception as e:
        print(f"Error: {e}")
        with open("debug_photo.txt", "a") as f:
            f.write(f"Error: {e}\n")
