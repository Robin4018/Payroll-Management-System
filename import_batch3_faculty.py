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
    print("Starting Batch 3 Faculty Import...")
    
    tenant = Tenant.objects.first()
    if not tenant:
        print("No Tenant found!")
        return

    data = [
        {
            "department": "Department of Social Work",
            "staff": [
                {"name": "Dr. S. Sam Lovely Son", "qualification": "M.S.W., M.Phil.,Ph.D", "designation": "HOD"},
                {"name": "Dr.Mrs.T. Priyadarshini", "qualification": "M.Sc., M.S.W., M.Phil.,Ph.D", "designation": "Assistant Professor"},
                {"name": "Dr. Mrs.K. Prema Malini", "qualification": "M.S.W., D.B.M., M.Phil.,Ph.D", "designation": "Assistant Professor"},
                {"name": "Dr. J. John Wesley", "qualification": "M.S.W., M.Phil.,Ph.D", "designation": "Assistant Professor"},
                {"name": "Dr.Mrs. D.Sasikala Mary", "qualification": "M.S.W.,M.Phil.,Ph.D", "designation": "Assistant Professor"},
                {"name": "Mr. A.Francis Xavier", "qualification": "M.S.W.,", "designation": "Assistant Professor/NSS Programme Officer"},
                {"name": "Ms.Christina Jenifer", "qualification": "M.S.W.,", "designation": "Assistant Professor"},
                {"name": "Ms.Esther Phope", "qualification": "M.S.W", "designation": "Assistant Professor"},
            ]
        },
        {
            "department": "Mathematics",
            "staff": [
                {"name": "Lt. Mrs. T. Rachel Priskilla", "qualification": "M.Sc., B.Ed.,", "designation": "Assistant Professor & NCC Officer(Girls Wing) - HOD Incharge"},
                {"name": "Mrs. D. Poornima Brichilal", "qualification": "M.Sc.,B.Ed.,M.Phil", "designation": "Assistant Professor"},
                {"name": "Mrs. Jayanthi", "qualification": "M.Sc.,", "designation": "Assistant Professor"},
                {"name": "Ms.Jaculin", "qualification": "M.Sc.,", "designation": "Assistant Professor"},
                {"name": "Ms.Merlin Swetha", "qualification": "M.Sc.,", "designation": "Assistant Professor"},
                {"name": "Mr.Balaji", "qualification": "M.Sc.,", "designation": "Assistant Professor"},
            ]
        },
        {
            "department": "Department of English",
            "staff": [
                {"name": "Dr.Mrs. J. Esther Margaret", "qualification": "M.A.,M.Phil.,Ph.D", "designation": "H.O.D"},
                {"name": "Dr.Mrs.E.Arokya Shylaja", "qualification": "M.A.,M.Phil.,Ph.D", "designation": "Assistant Professor"},
                {"name": "Dr.D.Franklin Vaseekaran", "qualification": "M.A.,M.Phil.,Ph.D", "designation": "Assistant Professor-NSS Programme Officer"},
                {"name": "Dr.J.Arul", "qualification": "M.A.,M.Ed.,M.Phil.,PGDCA.,Ph.D", "designation": "Assistant Professor"},
                {"name": "Dr.P.Joshua Christopher", "qualification": "M.A.,B.Ed.,Ph.D", "designation": "Assistant Professor"},
                {"name": "Dr.Mrs.P.Steffi Evangeline", "qualification": "M.A.,B.Ed.,M.Phil.,Ph.D", "designation": "Assistant Professor"},
                {"name": "Dr.Mrs.A.Stella", "qualification": "M.A.,M.Phil.,Ph.D", "designation": "Assistant Professor"},
                {"name": "Dr.Ms.U.Nithya Kumari", "qualification": "M.A.,M.Phil.,Ph.D", "designation": "Assistant Professor"},
                {"name": "Mr.Immanuel Deva Prathap", "qualification": "M.A.,M.Phil", "designation": "Assistant Professor"},
            ]
        },
        {
            "department": "Languages",
            "staff": [
                {"name": "Dr.Mrs. I. Prema John", "qualification": "M.A., M.Phil., B.Ed.,Ph.D", "designation": "Associate Professor.HOD(Tamil)"},
                {"name": "Dr.Mrs.G. Irene", "qualification": "M.A.,M.Phil.,B.Ed.,Ph.D", "designation": "Assistant Professor (Tamil)"},
                {"name": "Dr.Mrs. Umarani", "qualification": "M.A.,M.Phil.,Ph.D", "designation": "Assistant Professor (Tamil)"},
                {"name": "Dr.Samuel Babu", "qualification": "M.A.,M.Phil.,Ph.D", "designation": "Assistant Professor (Tamil)"},
                {"name": "Mrs. Ananthi", "qualification": "M.A.,M.Phil.,B.Ed.,", "designation": "Assistant Professor (Tamil)"},
                {"name": "Mrs. P. Agnes", "qualification": "M.A.,M.Phil.,B.Ed.,Dip.French", "designation": "Assistant Professor (French)- Part Time"},
                {"name": "Mrs.Gertrude Ravinayagam", "qualification": "M.A.(Hindi)", "designation": "Assistant Professor (Hindi)-Part Time"},
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
