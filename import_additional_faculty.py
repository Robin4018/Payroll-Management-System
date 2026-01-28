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
    print("Starting Additional Faculty Import...")
    
    tenant = Tenant.objects.first()
    if not tenant:
        print("No Tenant found!")
        return

    data = [
        {
            "department": "Department of Management",
            "staff": [
                {"name": "Dr. Praveen Kumar", "qualification": "M.B.A., M.Phil.Ph.D", "designation": "HOD incharge"},
                {"name": "Dr. Mrs. Preetha F. James", "qualification": "M.Sc.,M.B.A.,Ph.D", "designation": "Assistant Professor"},
                {"name": "Dr.Bennita Edward", "qualification": "M.B.A.,Ph.D", "designation": "Assistant Professor"},
                {"name": "Ms.Logasri", "qualification": "M.B.A.,", "designation": "Assistant Professor"},
                {"name": "Ms.Sophia", "qualification": "M.B.A.", "designation": "Assistant Professor"},
            ]
        },
        {
            "department": "Department of Visual Communication",
            "staff": [
                {"name": "Mrs. Sindhu", "qualification": "M.Sc VISCOM", "designation": "HOD Incharge"},
                {"name": "Mr. Roopan Babu", "qualification": "M.A.(English Litt).,M.Sc(VISCOM)", "designation": "Assistant Professor"},
                {"name": "Ms.Tharunika.R", "qualification": "B.Sc.,M.A(Mass Communication)", "designation": "Assistant Professor"},
                {"name": "Mr. Samson Dani Kiruba", "qualification": "B.Sc.,M.A.,", "designation": "Assistant Professor"},
                {"name": "Mr.Illango", "qualification": "B.Sc(VISCOM).,", "designation": "Technical Staff"},
            ]
        }
    ]

    for dept_data in data:
        dept_name = dept_data['department']
        dept, created = Department.objects.get_or_create(
            name=dept_name,
            tenant=tenant,
            defaults={'description': f"Department of {dept_name}"}
        )
        if created:
            print(f"Created Department: {dept.name}")
        else:
            print(f"Using Department: {dept.name}")

        for staff in dept_data['staff']:
            name_parts = staff['name'].split(' ')
            first_name = name_parts[0] + " " + (name_parts[1] if len(name_parts) > 1 else "")
            
            safe_name = slugify(staff['name'])
            email = f"{safe_name}@example.com"
            
            while Employee.objects.filter(email=email).exists():
                 email = f"{safe_name}{random.randint(1,999)}@example.com"
            
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
