import os
import django
import sys

# Setup Django Environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from employees.models import Designation, Employee
from django.db.models import Q

def rename_designation():
    # Target variations to rename
    targets = ["Lab Incharge – MCA Lab", "Lab Incharge - MCA Lab", "Lab Incharge MCA Lab"]
    new_name = "Lab Incharge"
    
    print(f"Renaming {targets} to '{new_name}'...")
    
    # 1. Update Designation Models
    # Check if 'Lab Incharge' already exists to avoid duplicates
    existing_dest = Designation.objects.filter(name=new_name).first()
    
    desigs = Designation.objects.filter(name__in=targets)
    count_desigs = desigs.count()
    
    if count_desigs > 0:
        if existing_dest:
            print(f"Target designation '{new_name}' already exists. Merging...")
            # Reassign employees pointing to old desigs to the existing one
            for d in desigs:
                Employee.objects.filter(designation_fk=d).update(designation_fk=existing_dest)
                d.delete() # Remove old
        else:
            print(f"Renaming {count_desigs} designations...")
            desigs.update(name=new_name)
    else:
        print("No Designation objects found with exact target names.")
        
    # 2. Update Employee String Fields (Legacy/Backup field)
    # Using Q objects for loose matching on the string field
    q_filter = Q()
    for t in targets:
        q_filter |= Q(designation__icontains=t)
        
    employees = Employee.objects.filter(q_filter)
    count_emps = employees.count()
    
    if count_emps > 0:
        print(f"Updating {count_emps} employee string records...")
        # Be careful not to rename generic strings incorrectly if they are just substrings
        # But 'Lab Incharge - MCA Lab' is specific enough.
        for emp in employees:
            if any(t.lower() in emp.designation.lower() for t in targets):
                print(f"Updating string for {emp.first_name}: {emp.designation} -> {new_name}")
                emp.designation = new_name
                emp.save()
    else:
        print("No employees found with matching string designation.")

    print("Rename complete.")

if __name__ == "__main__":
    rename_designation()
