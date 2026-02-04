import os
import django
import sys

# Setup Django Environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from employees.models import Employee

def check_missing_ctc():
    # We'll check for employees who weren't updated in the "bulk" run or have 0 CTC.
    # Since I forced update, let's look for designations not in the 'data' map essentially.
    
    # Actually, simpler: List unique designations of currently active employees
    # and cross reference with our known list.
    
    employees = Employee.objects.filter(is_active=True)
    all_designations = set()
    for e in employees:
        d = e.designation_fk.name if e.designation_fk else e.designation
        if d:
            all_designations.add(d.strip())
            
    # List from previous script (I'll just re-declare the keys here to check against)
    # Ideally I'd import, but copying for speed/isolation
    known_keys = [
        "Vice Principal / HOD", "HOD (General)", "H.O.D.", "HOD Incharge",
        "Associate Professor / HOD (Tamil)", "H.O.D. Commerce", "HOD Commerce with CA", 
        "HOD Commerce with PA", "Assistant Professor & NCC Officer (Girls Wing) – HOD Incharge",
        "Associate Professor", "Associate Professor – Commerce with CA / Librarian",
        "Assistant Professor", "Assistant Professor – Commerce", "Assistant Professor – Commerce with CA",
        "Assistant Professor – Commerce with PA", "Assistant Professor (Tamil)", 
        "Assistant Professor / NSS Programme Officer", "Assistant Professor – NSS Programme Officer",
        "Assistant Professor (French) – Part Time", "Assistant Professor (Hindi) – Part Time",
        "Director of Physical Education", "Physical Director", "Librarian", 
        "Assistant Librarian", "Library Assistant", "System Administrator", 
        "Lab Incharge – MCA Lab", "Lab Assistant", "Technical Staff"
    ]
    
    missing = []
    
    for desig in all_designations:
        # Check exact and fuzzy
        matched = False
        desig_norm = desig.lower()
        
        for k in known_keys:
            k_norm = k.lower()
            if desig_norm == k_norm:
                matched = True
                break
            # Logic from previous fuzzy script:
            if k_norm in desig_norm or desig_norm in k_norm:
                 matched = True
                 break
        
        if not matched:
            print(f"MISSING CONFIG: {desig}")

check_missing_ctc()
