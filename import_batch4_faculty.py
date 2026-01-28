import os
import django
import sys
import random

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings') 
django.setup()

from employees.models import Employee, Department, Designation
from tenants.models import Tenant
from django.utils.text import slugify
from datetime import date

def run():
    print("Starting Batch 4 Faculty Import...")
    
    tenant = Tenant.objects.first()
    if not tenant:
        print("No Tenant found!")
        return

    data = [
        {
            "department": "Department of Physical Education",
            "staff": [
                {"name": "Mr. Wesley Rajkumar", "qualification": "M.A., CPEd., MPEd.", "designation": "Director of Physical Education"},
                {"name": "Mr.Maniraj", "qualification": "B.A.,D.PEd.", "designation": "Physical Director"},
            ]
        },
        {
            "department": "Library",
            "staff": [
                {"name": "Dr.Sam Jeyachandran", "qualification": "MLISC.,M.Com.,Ph.D.", "designation": "Librarian"},
                {"name": "Mrs. Rajkala", "qualification": "RNRM.,CLIS.,B.A.,BLIS", "designation": "Assistant Librarian"},
                {"name": "Mr.Marsheel", "qualification": "MSW", "designation": "Library Assistant"},
            ]
        }
    ]

    for dept_data in data:
        dept_name = dept_data['department']
        dept, created = Department.objects.get_or_create(
            name=dept_name,
            tenant=tenant,
            defaults={'description': f"{dept_name}"}
        )
        if created:
            print(f"Created Department: {dept.name}")
        else:
            print(f"Using Department: {dept.name}")

        for staff in dept_data['staff']:
            # Unique email logic
            safe_name = slugify(staff['name'])
            base_email = f"{safe_name}"
            email = f"{base_email}@example.com"
            counter = 1
            while Employee.objects.filter(email=email).exists():
                 email = f"{base_email}{counter}@example.com"
                 counter += 1
            
            desig_name = staff['designation']
            designation, _ = Designation.objects.get_or_create(
                name=desig_name,
                tenant=tenant,
                defaults={'department': dept}
            )

            try:
                emp = Employee.objects.create(
                    tenant=tenant,
                    department=dept,
                    designation_fk=designation,
                    designation=desig_name,
                    first_name=staff['name'], 
                    last_name="", 
                    email=email,
                    phone=f"9{random.randint(100000000, 999999999)}",
                    qualification=staff['qualification'],
                    date_of_joining=date(2025, 6, 1),
                    employment_type=Employee.EmploymentType.PERMANENT,
                    ctc=600000.00
                )
                print(f"Created Employee: {emp.first_name}")
            except Exception as e:
                print(f"Error creating {staff['name']}: {e}")

if __name__ == '__main__':
    run()
