import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.append(os.getcwd())
django.setup()

from employees.models import Employee

def audit_names():
    print("--- Auditing Employee Names ---")
    
    # Check for empty last names
    empty_last = Employee.objects.filter(last_name__in=['', None])
    print(f"Employees with empty Last Name: {empty_last.count()}")
    
    for emp in empty_last[:5]:
        print(f"ID: {emp.id} | Name: '{emp.first_name}'")

    print("\n--- Auto-Fix Preview ---")
    # Preview split
    for emp in empty_last[:10]:
        full = emp.first_name.strip()
        if ' ' in full:
            parts = full.rsplit(' ', 1) # Split from right to get last identifier as Last Name? 
            # Or standard split?
            # "Mr. G. Paul Suthan" -> First: "Mr. G. Paul", Last: "Suthan"
            
            # Common Indian format might have initials at end too "Suthan G"
            # But "Mr. G. Paul Suthan" looks like First Middle Last.
            
            fname = parts[0]
            lname = parts[1]
            print(f"Original: '{full}' -> First: '{fname}', Last: '{lname}'")
        else:
            print(f"Original: '{full}' -> Cannot split (No space)")

if __name__ == '__main__':
    audit_names()
