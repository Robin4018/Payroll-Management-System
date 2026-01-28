import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.append(os.getcwd())
django.setup()

from employees.models import Employee

def fix_names():
    print("--- Fixing Employee Names ---")
    
    # Check for empty last names
    employees = Employee.objects.filter(last_name__in=['', None])
    print(f"Employees to process: {employees.count()}")
    
    count = 0
    for emp in employees:
        full = emp.first_name.strip()
        if ' ' in full:
            parts = full.rsplit(' ', 1)
            fname = parts[0].strip()
            lname = parts[1].strip()
            
            print(f"Fixing ID {emp.id}: '{full}' -> First: '{fname}', Last: '{lname}'")
            
            emp.first_name = fname
            emp.last_name = lname
            emp.save()
            count += 1
        else:
            print(f"Skipping ID {emp.id}: '{full}' (No space to split)")

    print(f"\nSuccessfully updated {count} employee records.")

if __name__ == '__main__':
    fix_names()
