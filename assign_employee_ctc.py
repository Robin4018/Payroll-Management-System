import os
import django
import sys
import random

# Setup Django Environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from employees.models import Employee, Designation

def parse_ctc(ctc_str):
    """
    Parses CTC strings like "₹7.0 – ₹12.0 L" to (700000, 1200000)
    """
    try:
        clean = ctc_str.replace('₹', '').replace(' L', '').strip()
        parts = clean.split('–')
        if len(parts) == 2:
            min_val = float(parts[0].strip()) * 100000
            max_val = float(parts[1].strip()) * 100000
            return min_val, max_val
        return 0, 0
    except:
        return 0, 0

data = {
    # Executives / HODs
    "Vice Principal / HOD": "₹7.0 – ₹12.0 L",
    "Vice Principal/HOD": "₹7.0 – ₹12.0 L", # Calculated missing
    "HOD (General)": "₹5.0 – ₹9.0 L",
    "H.O.D.": "₹5.0 – ₹9.0 L",
    "HOD Incharge": "₹4.0 – ₹7.0 L",
    "Associate Professor / HOD (Tamil)": "₹5.5 – ₹9.0 L",
    "H.O.D. Commerce": "₹6.0 – ₹9.5 L",
    "HOD Commerce with CA": "₹6.5 – ₹10.0 L",
    "HOD Commerce with PA": "₹6.0 – ₹9.0 L",
    "Assistant Professor & NCC Officer (Girls Wing) – HOD Incharge": "₹4.5 – ₹7.5 L",

    # Associate Professors
    "Associate Professor": "₹4.5 – ₹8.0 L",
    "Associate Professor – Commerce with CA / Librarian": "₹4.5 – ₹8.0 L",

    # Assistant Professors (Full-Time)
    "Assistant Professor": "₹2.5 – ₹5.5 L",
    "Assistant Professor – Commerce": "₹2.5 – ₹5.5 L",
    "Assistant Professor – Commerce with CA": "₹3.0 – ₹6.0 L",
    "Assistant Professor – Commerce with PA": "₹2.8 – ₹5.8 L",
    "Assistant Professor (Tamil)": "₹2.4 – ₹5.0 L",
    "Assistant Professor / NSS Programme Officer": "₹2.8 – ₹5.8 L",
    "Assistant Professor – NSS Programme Officer": "₹2.8 – ₹5.8 L",

    # Part-Time Faculty
    "Assistant Professor (French) – Part Time": "₹0.9 – ₹2.0 L",
    "Assistant Professor (Hindi) – Part Time": "₹0.9 – ₹2.0 L",

    # Physical Education
    "Director of Physical Education": "₹3.0 – ₹6.0 L",
    "Physical Director": "₹2.5 – ₹5.0 L",

    # Library Staff
    "Librarian": "₹3.0 – ₹6.0 L",
    "Assistant Librarian": "₹2.0 – ₹4.0 L",
    "Library Assistant": "₹1.6 – ₹3.0 L",

    # Technical / Non-Teaching Staff
    "System Administrator": "₹2.2 – ₹5.0 L",
    "Lab Incharge": "₹2.5 – ₹4.5 L",
    "Lab Incharge - MCA Lab": "₹2.5 – ₹4.5 L", # Keep for legacy matching if needed, or remove? Better to map new name.
    "Lab Assistant": "₹1.5 – ₹3.2 L",
    "Technical Staff": "₹1.8 – ₹4.0 L"
}

def assign_ctc_to_employees():
    employees = Employee.objects.filter(is_active=True).select_related('designation_fk')
    updated_count = 0
    
    print(f"Assigning CTCs for {employees.count()} employees...")

    for emp in employees:
        desig_name = ""
        
        # Determine designation name from FK or char field
        if emp.designation_fk:
            desig_name = emp.designation_fk.name
        elif emp.designation:
            desig_name = emp.designation
        
        if not desig_name:
            continue

        if not desig_name:
            continue
            
        # Normalize
        desig_norm = desig_name.lower().strip()
        
        # Exact match attempt
        ctc_range = data.get(desig_name)
        
        # Fuzzy / Partial Match
        if not ctc_range:
            # Sort data keys by length (desc) to match most specific first
            sorted_keys = sorted(data.keys(), key=len, reverse=True)
            for k in sorted_keys:
                k_norm = k.lower()
                # Check for containment
                if k_norm in desig_norm or desig_norm in k_norm:
                    ctc_range = data[k]
                    print(f"Fuzzy Match: '{desig_name}' -> '{k}'")
                    break
                    
        if ctc_range:
            min_val, max_val = parse_ctc(ctc_range)
            
            # Update if CTC is 0 OR if we want to force update (let's assume update if 0 for now to avoid overwriting real data)
            # Actually, user said "add these CTC to staffs", implies setting it.
            # Let's check: if CTC is < min_val, update it? Or just if 0?
            # Let's stick to update if 0 or default (e.g. < 10000)
            
            # Force Update for Demo
            if emp.ctc < 10000 or True: 
                random_ctc = random.randint(int(min_val), int(max_val))
                random_ctc = round(random_ctc / 1000) * 1000
                
                emp.ctc = random_ctc
                emp.save()
                print(f"Updated {emp.first_name} {emp.last_name} ({desig_name}): ₹{random_ctc}")
                updated_count += 1
                
    print(f"Total Employees Updated: {updated_count}")

if __name__ == "__main__":
    assign_ctc_to_employees()
