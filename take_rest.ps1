$edgePath = "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
$outDir = "d:\Project\Payroll Management System\universal-payroll-system\exact_screenshots"

$urls = @(
    @("http://localhost:8000/auto-login/?user=robin&next=/dashboard/college/salary-structure/", "admin_salary_structure.png"),
    @("http://localhost:8000/auto-login/?user=robin&next=/dashboard/college/payroll-processing/", "admin_run_payroll.png"),
    @("http://localhost:8000/auto-login/?user=robin&next=/dashboard/college/bank-payments/", "admin_bank_payments.png"),
    @("http://localhost:8000/auto-login/?user=robin&next=/dashboard/college/reimbursements/", "admin_reimbursements.png"),
    @("http://localhost:8000/auto-login/?user=robin&next=/dashboard/college/reports/", "admin_reports.png"),
    @("http://localhost:8000/auto-login/?user=capt-d-sudhakar@example.com&next=/dashboard/staff/", "staff_dashboard.png"),
    @("http://localhost:8000/auto-login/?user=capt-d-sudhakar@example.com&next=/dashboard/staff/profile/", "staff_profile.png"),
    @("http://localhost:8000/auto-login/?user=capt-d-sudhakar@example.com&next=/dashboard/staff/leaves/", "staff_leaves.png"),
    @("http://localhost:8000/auto-login/?user=capt-d-sudhakar@example.com&next=/dashboard/staff/payslips/", "staff_payslips.png"),
    @("http://localhost:8000/auto-login/?user=capt-d-sudhakar@example.com&next=/dashboard/staff/attendance/", "staff_attendance.png"),
    @("http://localhost:8000/auto-login/?user=capt-d-sudhakar@example.com&next=/dashboard/staff/reimbursements/", "staff_reimbursements.png")
)

foreach ($item in $urls) {
    $url = $item[0]
    $filename = $item[1]
    $fullPath = Join-Path $outDir $filename
    Write-Host "Capturing $filename ..."
    # Use direct call with try/catch to continue on error
    try {
        & $edgePath --headless --screenshot="$fullPath" --window-size=1920,1080 --hide-scrollbars --disable-gpu --virtual-time-budget=3000 "$url"
    } catch {
        Write-Host "Error capturing $filename"
    }
    Write-Host "Done $filename"
    Start-Sleep -Seconds 1
}
