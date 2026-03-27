from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable, Image as RLImage
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
import os
import pandas as pd
from django.conf import settings

def generate_payslip(payroll_ledger):
    file_name = f"payslip_{payroll_ledger.employee.id}_{payroll_ledger.month}.pdf"
    save_path = os.path.join(settings.BASE_DIR, 'media', 'payslips', file_name)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
    # Paths for signature and seal
    assets_dir = os.path.join(settings.BASE_DIR, 'media', 'assets', 'branding')
    sign_img_path = os.path.join(assets_dir, 'payslip_signature.png')

    # Document Setup
    doc = SimpleDocTemplate(save_path, pagesize=A4, 
                            rightMargin=40, leftMargin=40, 
                            topMargin=40, bottomMargin=40)
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom Styles
    maroon = colors.HexColor('#800000')
    navy = colors.HexColor('#1a237e')
    muted = colors.HexColor('#64748b')

    style_org_top = ParagraphStyle('OrgTop', parent=styles['Normal'], alignment=1, fontSize=8, textColor=colors.black, fontName='Helvetica-Bold')
    style_org_main = ParagraphStyle('OrgMain', parent=styles['Normal'], alignment=1, fontSize=20, textColor=maroon, fontName='Helvetica-Bold', leading=24)
    style_org_sub = ParagraphStyle('OrgSub', parent=styles['Normal'], alignment=1, fontSize=8, textColor=colors.black, fontName='Helvetica')
    style_officials = ParagraphStyle('Officials', parent=styles['Normal'], alignment=1, fontSize=11, textColor=maroon, fontName='Helvetica-Bold')
    style_roles = ParagraphStyle('Roles', parent=styles['Normal'], alignment=1, fontSize=8, textColor=colors.black, fontName='Helvetica')

    # 1. Header Reconstruction (High Fidelity)
    elements.append(Paragraph("CHURCH OF SOUTH INDIA TRUST ASSOCIATION - COIMBATORE DIOCESE", style_org_top))
    elements.append(Spacer(1, 0.05*inch))
    elements.append(Paragraph("BISHOP APPASAMY COLLEGE OF ARTS & SCIENCE", style_org_main))
    elements.append(Paragraph("(Affiliated to Bharathiar University, Approved by AICTE - New Delhi)", style_org_sub))
    elements.append(Paragraph("(Accredited by NAAC, ISO 9001 : 2015 Certified)", style_org_sub))
    elements.append(Paragraph("Recognized by UGC, New Delhi under Section 2(f) and 12(B)", style_org_sub))
    
    elements.append(Spacer(1, 0.15*inch))
    
    # Officials Row
    official_data = [
        [
            Paragraph("Rt.Rev. TIMOTHY RAVINDER, <font size=8>B.Sc., B.D.,</font>", style_officials), 
        ],
        [
            Paragraph("Chairman & Bishop in Coimbatore", style_roles)
        ]
    ]
    t_officials = Table(official_data, colWidths=[7.5*inch])
    elements.append(t_officials)

    official_lower = [
        [
            Paragraph("Rev. L. DAVID BARNABAS, <font size=7>M.A., B.D.,</font>", style_officials),
            Paragraph("Dr. Mrs. JEMIMAH WINSTON, <font size=7>M.Com., M.Phil., Ph.D.,</font>", style_officials)
        ],
        [
            Paragraph("Secretary", style_roles),
            Paragraph("Principal", style_roles)
        ]
    ]
    t_lower = Table(official_lower, colWidths=[3.75*inch, 3.75*inch])
    elements.append(t_lower)
    
    # Double Line Decoration
    elements.append(Spacer(1, 5))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=navy, spaceBefore=1, spaceAfter=1))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=navy, spaceBefore=1, spaceAfter=10))

    # 2. Payslip Body
    title_style = ParagraphStyle('PayslipTitle', parent=styles['Title'], alignment=1, fontSize=14, textColor=colors.black, fontName='Helvetica-Bold', spaceBefore=20, spaceAfter=20)
    elements.append(Paragraph(f"PAYSLIP FOR {payroll_ledger.month.strftime('%B %Y').upper()}", title_style))
    
    # Employee Details
    emp = payroll_ledger.employee
    emp_data = [
        ["EMPLOYEE NAME:", f"{emp.first_name} {emp.last_name}", "EMPLOYEE CODE:", emp.employee_code or "-"],
        ["DEPARTMENT:", emp.department.name if emp.department else "-", "DESIGNATION:", emp.designation or "-"],
        ["BANK A/C NO:", getattr(emp, 'bank_details', 'N/A'), "DATE OF JOINING:", emp.date_of_joining.strftime("%d-%m-%Y") if emp.date_of_joining else "-"]
    ]
    t_emp = Table(emp_data, colWidths=[1.5*inch, 2.5*inch, 1.5*inch, 1.8*inch])
    t_emp.setStyle(TableStyle([
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
        ('FONTNAME', (0,0), (0,-1), 'Helvetica-Bold'),
        ('FONTNAME', (2,0), (2,-1), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.lightgrey),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    elements.append(t_emp)
    elements.append(Spacer(1, 0.3*inch))
    
    # Financials
    fin_data = [["DESCRIPTION", "EARNINGS", "DESCRIPTION", "DEDUCTIONS"]]
    fin_data.append(["Basic Salary & Allowances", f"₹ {payroll_ledger.total_earnings:,.2f}", "General Deductions", f"₹ {payroll_ledger.total_deductions:,.2f}"])
    fin_data.append(["", "", "", ""])
    fin_data.append(["GROSS EARNINGS", f"₹ {payroll_ledger.total_earnings:,.2f}", "TOTAL DEDUCTIONS", f"₹ {payroll_ledger.total_deductions:,.2f}"])
    
    t_fin = Table(fin_data, colWidths=[2.2*inch, 1.3*inch, 2.2*inch, 1.3*inch])
    t_fin.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('BACKGROUND', (0,0), (-1,0), navy),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('ALIGN', (1,0), (1,-1), 'RIGHT'),
        ('ALIGN', (3,0), (3,-1), 'RIGHT'),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
        ('BACKGROUND', (0,-1), (-1,-1), colors.whitesmoke),
    ]))
    elements.append(t_fin)
    
    # Net Pay
    elements.append(Spacer(1, 0.15*inch))
    t_net = Table([["NET PAYABLE (INR):", f"₹ {payroll_ledger.net_pay:,.2f}"]], colWidths=[2.2*inch, 4.8*inch])
    t_net.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 1, colors.black),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('BACKGROUND', (0,0), (0,0), navy),
        ('TEXTCOLOR', (0,0), (0,0), colors.whitesmoke),
        ('ALIGN', (1,0), (1,0), 'CENTER'),
    ]))
    elements.append(t_net)

    # 3. Footer & Authentication
    elements.append(Spacer(1, 0.4*inch))
    
    # Re-insert the Signature and Seal image (PNG version with transparency)
    if os.path.exists(sign_img_path):
        sign_img = RLImage(sign_img_path, width=3.2*inch, height=1.6*inch)
        sign_img.hAlign = 'LEFT'
        elements.append(sign_img)

    # Bottom Contact Bar
    def add_contact_footer(canvas, doc):
        canvas.saveState()
        canvas.setStrokeColor(navy)
        canvas.line(40, 60, 555, 60)
        canvas.setFont('Helvetica', 7)
        footer_text = "129, Race Course, Coimbatore - 641 018, Tamil Nadu. | Ph: 0422 - 2221840 | Email: csibacas@gmail.com | www.csibacas.org"
        canvas.drawCentredString(A4[0]/2, 45, footer_text)
        canvas.drawCentredString(A4[0]/2, 35, "Head Office : CSI Coimbatore Diocesan Council, 256, Race Course, Coimbatore - 641 018.")
        canvas.restoreState()

    doc.build(elements, onFirstPage=add_contact_footer)
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
    
    # Graceful handling for empty records
    if not ledgers:
        file_name = "payroll_summary_empty.xlsx"
        save_path = os.path.join(settings.BASE_DIR, 'media', 'reports', file_name)
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        pd.DataFrame([{"Message": "No records found for this period"}]).to_excel(save_path, index=False)
        return f"/media/reports/{file_name}"

    file_name = f"payroll_summary_{ledgers[0].month}.xlsx"
    save_path = os.path.join(settings.BASE_DIR, 'media', 'reports', file_name)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    
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
