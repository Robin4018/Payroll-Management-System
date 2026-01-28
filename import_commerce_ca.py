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
    print("Starting Commerce CA Import...")
    
    tenant = Tenant.objects.first()
    if not tenant:
        print("No Tenant found!")
        return

    # Same list as Commerce, but distinct Department
    dept_name = "Department of Commerce with CA"
    
    staff_list = [
        {"name": "Mr. A.V. Ravi", "qualification": "M.Com., M.Phil.,", "designation": "H.O.D. Commerce"},
        {"name": "Dr.Mrs. Mobi Rajendran S", "qualification": "M.Com., M.Phil.,Ph.D", "designation": "HOD Commerce with CA"},
        {"name": "Mrs. G. Baby Cellin", "qualification": "M.Com.,M.Phil.,PGDCA.", "designation": "HOD Commerce with PA"},
        {"name": "Dr.Jenifer Janani", "qualification": "M.Com.,M.Phil.,PGDCA.,Ph.D", "designation": "Assistant Professor- Commerce with CA"},
        {"name": "Dr.Franklin Jebaraj", "qualification": "M.Com.,B.Ed.,M.Phil.,Ph.D", "designation": "Assistant Professor Commerce with CA"},
        {"name": "Dr.Sam Jeyachandran", "qualification": "M.Com.,MBA.,M.Phil.,B.Ed.,M.Lis.,Ph.D.,", "designation": "Associate Professor- Commerce with CA/Librariyan"},
        {"name": "Mrs.Kalaimani", "qualification": "M.Com.,B.Ed.,M.Phil.,", "designation": "Assistant Professor- Commerce with PA"},
        {"name": "Ms.Priskilla", "qualification": "M.Com.,", "designation": "Assistant Professor- Commerce"},
        {"name": "Mr.Jafferine", "qualification": "M.Com.,", "designation": "Assistant Professor- Commerce"},
        {"name": "Mr.Kiran", "qualification": "M.Com.,", "designation": "Assistant Professor- Commerce"},
        {"name": "Ms.Sindhya", "qualification": "M.Com.,", "designation": "Assistant Professor- Commerce"},
        {"name": "Mrs. Rajalakshmi", "qualification": "M.Com.,", "designation": "Assistant Professor- Commerce with CA"},
        {"name": "Ms.Christy", "qualification": "M.Com.,", "designation": "Assistant Professor- Commerce with CA"},
        {"name": "Mr.Godwin", "qualification": "M.Com.,", "designation": "Assistant Professor- Commerce with CA"},
        {"name": "Mrs.Sowmiya", "qualification": "M.Com.,", "designation": "Assistant Professor- Commerce with PA"},
        {"name": "Ms.Karishma", "qualification": "M.Com.,", "designation": "Assistant Professor- Commerce with PA"},
        {"name": "Dr.Sheela Hepziba", "qualification": "M.Com.,Ph.D.,", "designation": "Assistant Professor- Commerce with PA"},
    ]

    dept, created = Department.objects.get_or_create(
        name=dept_name,
        tenant=tenant,
        defaults={'description': f"{dept_name}"}
    )
    if created:
        print(f"Created Department: {dept.name}")
    else:
        print(f"Using Department: {dept.name}")

    for staff in staff_list:
        # We allow duplicate names now since it's a separate department request
        # But we still need unique emails.
        
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
            print(f"Created Employee: {emp.first_name} in {dept.name}")
        except Exception as e:
            print(f"Error creating {staff['name']}: {e}")

if __name__ == '__main__':
    run()
