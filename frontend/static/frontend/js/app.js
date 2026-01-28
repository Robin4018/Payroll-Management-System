const API_BASE = '/api';

// Auth Logic
const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        try {
            // Use the new session-aware login endpoint
            const res = await fetch('/api/login-session/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, password })
            });

            if (res.ok) {
                const data = await res.json();
                localStorage.setItem('access_token', data.access);
                localStorage.setItem('refresh_token', data.refresh);
                localStorage.setItem('username', username);
                localStorage.setItem('username', username);

                // Check for redirect param
                const urlParams = new URLSearchParams(window.location.search);
                const nextUrl = urlParams.get('next');

                if (nextUrl) {
                    window.location.href = nextUrl;
                } else {
                    window.location.href = '/dashboard/';
                }
            } else {
                document.getElementById('loginError').innerText = 'Invalid credentials';
            }
        } catch (err) {
            console.error(err);
            document.getElementById('loginError').innerText = 'Login Failed';
        }
    });
}

// Register Logic
const registerForm = document.getElementById('registerForm');
if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('reg-username').value;
        const email = document.getElementById('reg-email').value;
        const password = document.getElementById('reg-password').value;
        const errDiv = document.getElementById('regError');

        errDiv.innerText = '';

        try {
            const res = await fetch(`${API_BASE}/register/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ username, email, password })
            });

            const data = await res.json();

            if (res.ok) {
                // Auto login mechanism could be improved, but for now redirect to login
                // Or better, redirect to select-entity if we auto-logged in.

                // Let's assume user needs to login first as per current flow, 
                // but we should maybe redirect directly if we can return a token.
                // Sticking to original: "Registration Successful! Please Login."
                alert("Registration Successful! Please Login.");
                window.location.href = '/';
            } else {
                errDiv.innerText = data.error || 'Registration Failed';
            }
        } catch (err) {
            errDiv.innerText = 'Error connecting to server';
        }
    });
}

// Select Entity Logic
async function selectEntity(type) {
    try {
        const res = await authFetch(`${API_BASE}/set-profile/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ type: type })
        });

        const data = await res.json();

        if (res.ok) {
            window.location.href = data.redirect; // e.g., /dashboard/school/
        } else {
            document.getElementById('selectError').innerText = data.error || 'Failed to set profile';
            document.getElementById('selectError').classList.remove('hidden');
        }
    } catch (e) {
        console.error(e);
        alert("Error setting profile");
    }
}

// Dashboard Logic
if (window.location.pathname.includes('dashboard')) {
    checkAuth();
    loadDashboard();
}

async function checkAuth() {
    if (!localStorage.getItem('access_token')) {
        window.location.href = '/';
        return;
    }

    try {
        const res = await authFetch(`${API_BASE}/me/`);
        const user = await res.json();

        // Onboarding Check
        if (!user.organization_type && user.role !== 'employee') {
            // If not an employee and no organization type set, redirect to select entity
            // Avoid infinite loop if we are already on select-entity (handled by page check usually, but checkAuth is for dashboard)
            window.location.href = '/select-entity/';
            return;
        }

        localStorage.setItem('role', user.role);
        localStorage.setItem('employee_id', user.employee_id || '');
        if (user.organization_type) {
            localStorage.setItem('organization_type', user.organization_type);

            // Enforce correct dashboard type
            const correctPath = `/dashboard/${user.organization_type.toLowerCase()}/`;
            if (!window.location.pathname.includes(correctPath)) {
                window.location.href = correctPath;
                return;
            }
        }

        const userDisplay = document.getElementById('userDisplay');
        if (userDisplay) {
            userDisplay.innerText = user.employee_name || user.username;
        }

        const dateDisplay = document.getElementById('dateDisplay');
        if (dateDisplay) {
            dateDisplay.innerText = new Date().toLocaleDateString();
        }

        applyPermissions(user.role);
    } catch (e) {
        console.error("Auth check failed", e);
    }
}

function applyPermissions(role) {
    if (role === 'employee') {
        // HIDE Admin links
        const overviewLink = document.querySelector('a[onclick*="overview"]');
        if (overviewLink) overviewLink.style.display = 'none';

        const employeesLink = document.querySelector('a[onclick*="employees"]');
        if (employeesLink) employeesLink.style.display = 'none';

        // Hide Admin sections
        const overviewSec = document.getElementById('overview');
        if (overviewSec) overviewSec.classList.add('hidden');

        const empSec = document.getElementById('employees');
        if (empSec) empSec.classList.add('hidden');

        // Hide Run Payroll Form
        const actionPanel = document.querySelector('.action-panel');
        if (actionPanel) actionPanel.style.display = 'none';

        // Show Payroll History by default
        showSection('payroll');
    }
}

function logout() {
    localStorage.clear();
    window.location.href = '/';
}

function showSection(sectionId) {
    document.querySelectorAll('.content-section').forEach(el => el.classList.add('hidden'));
    const section = document.getElementById(sectionId);
    if (section) section.classList.remove('hidden');

    document.querySelectorAll('.sidebar nav a').forEach(el => el.classList.remove('active'));

    // Find link that corresponds to this section
    // Simple robust match
    const link = Array.from(document.querySelectorAll('.sidebar nav a')).find(a => a.getAttribute('onclick')?.includes(sectionId));
    if (link) link.classList.add('active');

    if (sectionId === 'employees') loadEmployees();
    if (sectionId === 'payroll') loadPayrollHistory();
}

async function authFetch(url, options = {}) {
    let token = localStorage.getItem('access_token');
    if (!options.headers) options.headers = {};
    options.headers['Authorization'] = `Bearer ${token}`;

    let res = await fetch(url, options);

    if (res.status === 401) {
        // Simple refresh logic or logout. detailed refresh is out of scope for tight timeline
        alert("Session expired. Please login again.");
        logout();
    }
    return res;
}

async function loadDashboard() {
    // Determine stats from API
    try {
        const res = await authFetch(`${API_BASE}/employees/`);
        const data = await res.json();
        document.getElementById('totalEmployees').innerText = data.count || data.results.length || 0;
    } catch (e) {
        console.error(e);
    }
}

async function loadEmployees() {
    const tbody = document.querySelector('#employeesTable tbody');
    tbody.innerHTML = '<tr><td colspan="5">Loading...</td></tr>';

    try {
        const res = await authFetch(`${API_BASE}/employees/`);
        const data = await res.json();
        const employees = data.results || data;

        tbody.innerHTML = employees.map(emp => `
            <tr>
                <td>${emp.first_name} ${emp.last_name}</td>
                <td>${emp.employee_code || '-'}</td>
                <td>${emp.designation || '-'}</td>
                <td><span class="badge">${emp.employment_type}</span></td>
                <td>${emp.is_active ? 'Active' : 'Inactive'}</td>
            </tr>
        `).join('');
    } catch (e) {
        tbody.innerHTML = '<tr><td colspan="5" class="error-msg">Failed to load data</td></tr>';
    }
}

async function runPayroll() {
    const btn = document.querySelector('.run-form button');
    const resultDiv = document.getElementById('payrollResult');
    const tenantId = document.getElementById('tenantSelect').value;
    const month = document.getElementById('payrollMonth').value;

    if (!month) {
        alert("Please select a month");
        return;
    }

    btn.disabled = true;
    btn.innerText = 'Processing...';
    resultDiv.innerText = '';

    try {
        const res = await authFetch(`${API_BASE}/payroll/run/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tenant_id: tenantId, month: month })
        });

        const data = await res.json();
        if (res.ok) {
            resultDiv.innerHTML = `<span style="color: #4ade80">${data.message}</span>`;
        } else {
            resultDiv.innerHTML = `<span class="error-msg">${data.error || 'Failed'}</span>`;
        }
    } catch (e) {
        resultDiv.innerText = "Error running payroll";
    } finally {
        btn.disabled = false;
        btn.innerText = 'Generate Payslips';
    }
}

async function exportExcel() {
    const tenantId = document.getElementById('tenantSelect').value;
    const month = document.getElementById('payrollMonth').value;

    if (!month) {
        alert("Please select a month");
        return;
    }

    try {
        const res = await authFetch(`${API_BASE}/payroll/export-excel/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ tenant_id: tenantId, month: month })
        });

        const data = await res.json();
        if (res.ok) {
            window.open(data.file_url, '_blank');
        } else {
            alert(data.error || 'Failed to export');
        }
    } catch (e) {
        alert("Error exporting excel");
    }
}

async function loadPayrollHistory() {
    const tbody = document.querySelector('#payrollTable tbody');
    tbody.innerHTML = '<tr><td colspan="5">Loading...</td></tr>';

    try {
        const res = await authFetch(`${API_BASE}/payroll/`);
        const data = await res.json();
        const records = data.results || data;

        tbody.innerHTML = records.map(p => `
            <tr>
                <td>${p.employee_name || 'Emp ' + p.employee}</td>
                <td>${p.month}</td>
                <td>${p.net_pay}</td>
                <td>${p.status}</td>
                <td>
                    <button onclick="viewPayslip(${p.id})" class="btn-primary" style="padding: 0.25rem 0.5rem; font-size: 0.8rem;">View PDF</button>
                </td>
            </tr>
        `).join('');
    } catch (e) {
        tbody.innerHTML = '<tr><td colspan="5" class="error-msg">Failed to load history</td></tr>';
    }
}

async function viewPayslip(id) {
    try {
        const res = await authFetch(`${API_BASE}/payroll/${id}/payslip/`);
        const data = await res.json();
        if (data.payslip) {
            window.open(data.payslip, '_blank');
        } else {
            alert("Payslip not found");
        }
    } catch (e) {
        alert("Error fetching payslip");
    }
}
