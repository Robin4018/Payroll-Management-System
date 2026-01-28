from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import pandas as pd
import os
from django.conf import settings

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import os
from django.conf import settings

def generate_payslip(payroll_ledger):
    file_name = f"payslip_{payroll_ledger.employee.id}_{payroll_ledger.month}.pdf"
    save_path = os.path.join(settings.BASE_DIR, 'media', 'payslips', file_name)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    doc = SimpleDocTemplate(save_path, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    # Header
    org_name = payroll_ledger.employee.tenant.name if payroll_ledger.employee.tenant else "Organization"
    elements.append(Paragraph(f"<b>{org_name}</b>", styles['Title']))
    elements.append(Paragraph(f"Payslip for {payroll_ledger.month.strftime('%B %Y')}", styles['Heading2']))
    elements.append(Spacer(1, 0.2*inch))
    
    # Employee Details
    emp = payroll_ledger.employee
    emp_data = [
        ["Employee Name:", f"{emp.first_name} {emp.last_name}", "Employee Code:", emp.employee_code or "-"],
        ["Department:", emp.department.name if emp.department else "-", "Designation:", emp.designation or "-"],
        ["Date of Joining:", emp.date_of_joining.strftime("%d-%m-%Y") if emp.date_of_joining else "-", "Bank A/c:", getattr(emp, 'bank_details', 'N/A')]
    ]
    t_emp = Table(emp_data, colWidths=[1.5*inch, 2.5*inch, 1.5*inch, 2*inch])
    t_emp.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(t_emp)
    elements.append(Spacer(1, 0.3*inch))
    
    # Earnings & Deductions Table
    # We need to fetch the breakdown. 
    # Ideally, PayrollLedger should store a JSON breakdown. 
    # For now, we will re-fetch structure or just show totals if JSON isn't available.
    # TODO: In a real system, use a JSONField on Ledger.
    # Here, we will just show the TOTALS as rows for simplicity OR try to reconstruct if possible.
    # Let's show a summary table for now.
    
    data = [
        ["Earnings", "Amount (Rs.)", "Deductions", "Amount (Rs.)"]
    ]
    
    # Placeholder for detailed breakdown
    # In V2, we should save the snapshot in Ledger.
    # For now:
    data.append(["Basic & Allowances", f"{payroll_ledger.total_earnings}", "PF/Tax/Other", f"{payroll_ledger.total_deductions}"])
    data.append(["", "", "", ""]) # Spacer row
    
    # Totals
    data.append(["Total Earnings", f"{payroll_ledger.total_earnings}", "Total Deductions", f"{payroll_ledger.total_deductions}"])
    
    t_main = Table(data, colWidths=[2.5*inch, 1.5*inch, 2.5*inch, 1.5*inch])
    t_main.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.grey),
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('ALIGN', (3,0), (3,-1), 'RIGHT'),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'), # Total row
    ]))
    elements.append(t_main)
    elements.append(Spacer(1, 0.2*inch))
    
    # Net Pay
    net_style = ParagraphStyle('NetPay', parent=styles['Heading2'], alignment=1, textColor=colors.navy)
    elements.append(Paragraph(f"Net Payable: Rs. {payroll_ledger.net_pay}", net_style))
    
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph("** This is a computer-generated document and does not require a signature. **", styles['Italic']))
    
    doc.build(elements)
    
    return f"/media/payslips/{file_name}"

def generate_payroll_excel(ledgers):
    """
    Generates an Excel file for the given list/queryset of payroll ledgers.
    """
    data = []
    for ledger in ledgers:
        data.append({
            'Employee Code': ledger.employee.employee_code,
            'Name': f"{ledger.employee.first_name} {ledger.employee.last_name}",
            'Month': ledger.month,
            'Total Earnings': ledger.total_earnings,
            'Total Deductions': ledger.total_deductions,
            'Net Pay': ledger.net_pay,
            'Status': ledger.status
        })
    
    df = pd.DataFrame(data)
    
    file_name = f"payroll_summary_{ledgers[0].month}.xlsx" if ledgers else "payroll_summary.xlsx"
    save_path = os.path.join(settings.BASE_DIR, 'media', 'reports', file_name)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    df.to_excel(save_path, index=False)
    df.to_excel(save_path, index=False)
    return f"/media/reports/{file_name}"

def generate_bank_transfer_file(ledgers):
    """
    Generates a CSV for Bank Disbursement.
    Format: Account No, IFSC, Amount, Name, Reference (Month)
    """
    data = []
    for ledger in ledgers:
        # Check if bank details exist
        bank = getattr(ledger.employee, 'bank_details', None)
        if bank:
            acc_no = bank.account_number
            ifsc = bank.ifsc_code
            name = bank.account_holder_name
        else:
            acc_no = "MISSING"
            ifsc = "MISSING"
            name = f"{ledger.employee.first_name} {ledger.employee.last_name}"
            
        data.append({
            'Beneficiary Account Number': acc_no,
            'Beneficiary Name': name,
            'IFSC Code': ifsc,
            'Amount': ledger.net_pay,
            'Narration': f"Salary {ledger.month.strftime('%b %Y')}"
        })
    
    df = pd.DataFrame(data)
    file_name = f"bank_transfer_{ledgers[0].month}.csv" if ledgers else "bank_transfer.csv"
    save_path = os.path.join(settings.BASE_DIR, 'media', 'reports', file_name)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    df.to_csv(save_path, index=False)
    return f"/media/reports/{file_name}"
