import os
import django
import sys
import random

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings') # Assuming backend.settings
django.setup()

from employees.models import Employee, Department, Designation
from tenants.models import Tenant
from django.utils.text import slugify
from datetime import date

def run():
    print("Starting Faculty Import...")
    
    # Get Tenant (Assuming the education one or first one)
    tenant = Tenant.objects.first()
    if not tenant:
        print("No Tenant found! Please create a tenant first.")
        return

    print(f"Using Tenant: {tenant.name}")

    data = [
         {
            "department": "Department of Computer Science",
            "staff": [
                {"name": "Mr. G. Paul Suthan", "qualification": "M.Sc., M.Phil.,(CSC).,(Ph.D)", "designation": "Vice Principal/HOD"},
                {"name": "Mrs. G. Arul Geetha", "qualification": "MCA., M.Phil.,(CSC)", "designation": "Associate Professor"},
                {"name": "Dr. Mrs.N. Sudha", "qualification": "MCA., M.Phil.,Ph.D.,(CSC)", "designation": "Associate Professor"},
                {"name": "Mrs. P. Dheepa", "qualification": "MCA., M.Phil.,(CSC)", "designation": "Associate Professor"},
                {"name": "Mrs. C. Ruby Gnanaselvam", "qualification": "MCA., M.Phil.,(CSC)", "designation": "Assistant Professor"},
                {"name": "Capt. D. Sudhakar", "qualification": "MCA., M.Phil., (Ph.D)(NCC Officer, Boys Wing)", "designation": "Assistant Professor"},
                {"name": "Dr. A.Edwin Rajesh", "qualification": "MCA., M.Phil. (CSC).,Ph.D", "designation": "Assistant Professor"},
                {"name": "Mrs. T. Selva Priya", "qualification": "M.Sc.,M.Phil.,(CSC)(Ph.D)", "designation": "Assistant Professor"},
                {"name": "Mrs. R. Sakila", "qualification": "MCA.,M.Phil.,(CSC)", "designation": "Assistant Professor"},
                {"name": "Miss.P. Mercy Augestina", "qualification": "M.C.A.,M.Phil.,(CSC)", "designation": "Assistant Professor"},
                {"name": "Mrs.A. Helen Nirmala", "qualification": "MCA", "designation": "Assistant Professor"},
                {"name": "Mrs. Sindhu Priyadharsini", "qualification": "M.C.A.,M.Phil.,(CSC)", "designation": "Assistant Professor"},
                {"name": "Mrs.Soundarya", "qualification": "MCA", "designation": "Assistant Professor"},
                {"name": "Ms. Glory Evangeline", "qualification": "MCA", "designation": "Assistant Professor"},
                {"name": "Mr. S. Lional Vijayaraj", "qualification": "DCA", "designation": "System Administrator"},
                {"name": "Mrs.Christina Bai Annapoorani", "qualification": "M.Sc .,B.Ed.,M.Phil.,(CSC)", "designation": "Lab Incharge - MCA Lab"},
            ]
        },
        {
            "department": "Department of Catering Science & Hotel Management",
            "staff": [
                {"name": "Dr. Edson Nirmal Christopher", "qualification": "B.Sc.,MBA.,Ph.D", "designation": "HOD"},
                {"name": "Mr.Suresh Kumar.P", "qualification": "B.Sc., MBA", "designation": "Assistant Professor"},
                {"name": "Mr.Sahaya Rooban", "qualification": "B.Sc.,MBA", "designation": "Assistant Professor"},
                {"name": "Mr.Muthu Selvam", "qualification": "B.Sc.", "designation": "Assistant Professor"},
            ]
        },
        {
            "department": "Department of Commerce",
            "staff": [
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
        },
        {
            "department": "Department of Costume Design & Fashion",
            "staff": [
                {"name": "Dr.Ms. R. Sheela John", "qualification": "M.Sc., M.Phil.,M.B.A.,Ph.D", "designation": "H.O.D."},
                {"name": "Mrs. Suba J.A", "qualification": "M.Tech., MBA", "designation": "Associate Professor"},
                {"name": "Mrs. K.Catherine Francis", "qualification": "P.G.Dip.PMIR, M.Sc.,M.Phil", "designation": "Assistant Professor"},
                {"name": "Mrs.Sharmila Devi", "qualification": "M.Sc.,.M.Phil", "designation": "Assistant Professor"},
                {"name": "Mrs.Sandhiya .P", "qualification": "M.Sc.,", "designation": "Assistant Professor"},
                {"name": "Mrs. Ruth Grace Samuel", "qualification": "M.Sc.,", "designation": "Assistant Professor"},
                {"name": "Mrs.Lydia Dharshini.S", "qualification": "M.Sc.,", "designation": "Assistant Professor"},
                {"name": "Ms.Souganthika", "qualification": "M.Sc.,", "designation": "Assistant Professor"},
                {"name": "Mrs.Mohanna Priya", "qualification": "Dip. in Fashion Technology", "designation": "Lab Assistant"},
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
            # Clean up the name a bit to get a decent last name
            if len(name_parts) > 2:
                last_name = " ".join(name_parts[2:])
            elif len(name_parts) > 1:
                last_name = name_parts[1]
            else:
                last_name = "Employee" # Fallback
            
            # Better name splitting logic to handle "Dr. Name Surname" or "Mr. Name"
            # It's fuzzy, but unique email generation is key.
            safe_name = slugify(staff['name'])
            email = f"{safe_name}@example.com"
            
            # Check for existing email to avoid crash, append random if needed
            while Employee.objects.filter(email=email).exists():
                 email = f"{safe_name}{random.randint(1,999)}@example.com"
            
            # Designation
            desig_name = staff['designation']
            designation, _ = Designation.objects.get_or_create(
                name=desig_name,
                tenant=tenant,
                defaults={'department': dept} # Assign to this dept by default if new
            )

            # Create Employee
            try:
                emp = Employee.objects.create(
                    tenant=tenant,
                    department=dept,
                    designation_fk=designation,
                    # legacy field
                    designation=desig_name,
                    first_name=staff['name'], # Put full name in first name to be safe with titles like "Dr. Mrs."
                    last_name="", 
                    email=email,
                    phone=f"9{random.randint(100000000, 999999999)}",
                    qualification=staff['qualification'],
                    date_of_joining=date(2025, 6, 1), # Approx academic year start
                    employment_type=Employee.EmploymentType.PERMANENT,
                    ctc=600000.00 # Placeholder
                )
                print(f"Created Employee: {emp.first_name} ({emp.qualification})")
            except Exception as e:
                print(f"Error creating {staff['name']}: {e}")

if __name__ == '__main__':
    run()
