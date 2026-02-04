import os
import django
import sys

# Setup Django Environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from employees.models import Employee

def check_specific():
    # Targets
    targets = ["Vice Principal", "HOD", "Lab Incharge"]
    
    print("Checking specific designations:")
    employees = Employee.objects.filter(is_active=True)
    
    found = False
    for e in employees:
        d = e.designation_fk.name if e.designation_fk else e.designation
        if not d: continue
        
        # Check if matches target
        is_target = any(t.lower() in d.lower() for t in targets)
        if is_target:
            print(f"Name: {e.first_name} {e.last_name}")
            print(f"Designation: {d}")
            print(f"CTC: {e.ctc}")
            print("-" * 20)
            found = True
            
    if not found:
        print("No matching employees found for verification.")

check_specific()
