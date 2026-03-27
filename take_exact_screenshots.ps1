$edgePath = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
$outDir = "d:\Project\Payroll Management System\universal-payroll-system\exact_screenshots"

if (!(Test-Path $outDir)) { mkdir $outDir }

$urls = @(
    @("http://localhost:8000/dashboard/college/", "admin_dashboard.png"),
    @("http://localhost:8000/dashboard/college/departments/", "admin_departments.png"),
    @("http://localhost:8000/dashboard/college/employees/", "admin_employees.png"),
    @("http://localhost:8000/dashboard/college/attendance/", "admin_attendance.png"),
    @("http://localhost:8000/dashboard/college/salary-structure/", "admin_salary_structure.png"),
    @("http://localhost:8000/dashboard/college/payroll-processing/", "admin_run_payroll.png"),
    @("http://localhost:8000/dashboard/college/bank-payments/", "admin_bank_payments.png"),
    @("http://localhost:8000/dashboard/college/reimbursements/", "admin_reimbursements.png"),
    @("http://localhost:8000/dashboard/college/reports/", "admin_reports.png"),
    @("http://localhost:8000/dashboard/staff/", "staff_dashboard.png"),
    @("http://localhost:8000/dashboard/staff/profile/", "staff_profile.png"),
    @("http://localhost:8000/dashboard/staff/leaves/", "staff_leaves.png"),
    @("http://localhost:8000/dashboard/staff/payslips/", "staff_payslips.png"),
    @("http://localhost:8000/dashboard/staff/attendance/", "staff_attendance.png"),
    @("http://localhost:8000/dashboard/staff/reimbursements/", "staff_reimbursements.png")
)

foreach ($item in $urls) {
    $url = $item[0]
    $filename = $item[1]
    $fullPath = Join-Path $outDir $filename
    Write-Host "Capturing $filename ..."
    & $edgePath --headless --screenshot="$fullPath" --window-size=1920,1080 --hide-scrollbars --disable-gpu --virtual-time-budget=5000 "$url"
    Write-Host "Done $filename"
}
