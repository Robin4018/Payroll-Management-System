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

                // --- CUSTOM ROLE ENFORCEMENT ---
                const loginModeInput = document.getElementById('login_mode_input');
                if (loginModeInput) {
                    const currentMode = loginModeInput.value; 
                    const userRole = data.role; 

                    console.log(`[Auth] Login Attempt: Mode=${currentMode}, Role=${userRole}, Super=${data.is_superuser}`);

                    if (data.is_superuser) {
                        console.log("[Auth] Superuser detected - skipping role enforcement");
                    } else {
                        if (currentMode === 'employee' && userRole === 'admin') {
                            const errEl = document.getElementById('loginError');
                            errEl.innerText = 'Administrative account detected. Please switch to the Admin tab above.';
                            errEl.classList.remove('hidden');
                            if (loginForm.querySelector('.btn-submit')) {
                                loginForm.querySelector('.btn-submit').innerHTML = 'Sign In <i class="fas fa-arrow-right"></i>';
                                loginForm.querySelector('.btn-submit').disabled = false;
                            }
                            return;
                        }

                        if (currentMode === 'admin' && userRole === 'employee') {
                            const errEl = document.getElementById('loginError');
                            errEl.innerText = 'Staff credentials detected. Please switch to the Employee tab above.';
                            errEl.classList.remove('hidden');
                            if (loginForm.querySelector('.btn-submit')) {
                                loginForm.querySelector('.btn-submit').innerHTML = 'Admin Sign In <i class="fas fa-key"></i>';
                                loginForm.querySelector('.btn-submit').disabled = false;
                            }
                            return;
                        }
                    }
                }
                // -------------------------------

                localStorage.setItem('access_token', data.access);
                localStorage.setItem('refresh_token', data.refresh);
                localStorage.setItem('username', username);
                localStorage.setItem('role', data.role);
                localStorage.setItem('employee_name', data.employee_name || '');
                if (data.employee_id) localStorage.setItem('employee_id', data.employee_id);

                // 2. Determine redirect - prioritized redirect parameter from URL
                const urlParams = new URLSearchParams(window.location.search);
                const nextUrl = urlParams.get('next');

                if (nextUrl) {
                    window.location.href = nextUrl;
                } else if (data.redirect) {
                    window.location.href = data.redirect;
                } else {
                    window.location.href = '/dashboard/';
                }
            } else {
                const errorData = await res.json();
                const errEl = document.getElementById('loginError');
                errEl.innerText = errorData.error || 'Invalid credentials';
                errEl.classList.remove('hidden');
            }
        } catch (err) {
            console.error("Login call failed:", err);
            const errEl = document.getElementById('loginError');
            errEl.innerText = 'Login Failed: Server Error';
            errEl.classList.remove('hidden');
        }
    });
}

// Register Logic
const registerForm = document.getElementById('registerForm');
if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const full_name = document.getElementById('reg-name').value;
        const email = document.getElementById('reg-email').value;
        const password = document.getElementById('reg-password').value;
        const errDiv = document.getElementById('regError');

        errDiv.innerText = '';

        try {
            const res = await fetch(`${API_BASE}/register/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    username: email, // Use email as unique username
                    email: email,
                    password: password,
                    full_name: full_name
                })
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
                errDiv.style.display = 'block';
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
    checkAuth().then(() => {
        loadDashboard();
    });
}

async function checkAuth() {
    // Immediate UI transformation based on cached role
    const cachedRole = localStorage.getItem('role');
    if (cachedRole) {
        applyPermissions(cachedRole);
    }

    if (!localStorage.getItem('access_token')) {
        window.location.href = '/logout/';
        return;
    }

    try {
        const res = await authFetch(`${API_BASE}/me/`);
        const user = await res.json();

        console.log("UserInfo from API:", user);

        // Default to COLLEGE if not specified
        const orgType = user.organization_type || 'COLLEGE';
        localStorage.setItem('role', user.role);
        localStorage.setItem('employee_id', user.employee_id || '');
        localStorage.setItem('employee_name', user.employee_name || '');
        localStorage.setItem('organization_type', orgType);

        // Enforce correct dashboard type
        let correctPath = `/dashboard/${orgType.toLowerCase()}/`;

        // Special routing for staff
        if (user.role === 'employee') {
            if (orgType === 'COMPANY') {
                correctPath = '/dashboard/company/staff/';
            } else {
                correctPath = '/dashboard/staff/';
            }
        }

        if (!window.location.pathname.includes(correctPath) && window.location.pathname.includes('/dashboard/')) {
            console.log("Redirecting to correct dashboard path:", correctPath);
            window.location.href = correctPath;
            return;
        }

        const nameDisplay = document.getElementById('header-user-name');
        const roleDisplay = document.getElementById('header-user-role');
        const initialsDisplay = document.getElementById('header-user-initials');

        if (nameDisplay) {
            const fullName = user.employee_name || user.username;
            nameDisplay.innerText = fullName;

            if (initialsDisplay) {
                const initials = fullName.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2);
                initialsDisplay.innerText = initials;
            }
        }
        if (roleDisplay) {
            roleDisplay.innerText = user.role === 'employee' ? 'Staff Member' : 'Administrator';
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
    console.log("Applying permissions for role:", role);
    if (role === 'employee') {
        const adminElements = document.querySelectorAll('.admin-only');
        console.log("Hiding", adminElements.length, "admin elements");
        adminElements.forEach(el => {
            el.classList.add('hidden');
            el.style.display = 'none';
        });

        const staffElements = document.querySelectorAll('.staff-only');
        console.log("Showing", staffElements.length, "staff elements");
        staffElements.forEach(el => {
            el.classList.remove('hidden');
            el.style.display = 'block';
            if (el.tagName === 'A') el.style.display = 'flex'; // Sidebar items usually flex
        });

        // Hide legacy sections if any
        ['overview', 'employees'].forEach(id => {
            const el = document.getElementById(id);
            if (el) {
                el.classList.add('hidden');
                el.style.display = 'none';
            }
        });

        // Show Payroll History by default if possible
        if (typeof showSection === 'function' && document.getElementById('payroll')) {
            showSection('payroll');
        }
    } else {
        // Admin View
        document.querySelectorAll('.admin-only').forEach(el => {
            el.classList.remove('hidden');
            el.style.display = '';
        });
        document.querySelectorAll('.staff-only').forEach(el => {
            el.classList.add('hidden');
            el.style.display = 'none';
        });
    }
}

function logout() {
    localStorage.clear();
    window.location.href = '/logout/';
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

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

async function authFetch(url, options = {}) {
    const token = localStorage.getItem('access_token');
    const headers = { ...options.headers };

    // Default to JSON for methods that usually carry a body
    const method = (options.method || 'GET').toUpperCase();
    if (['POST', 'PUT', 'PATCH'].includes(method) && !headers['Content-Type'] && !(options.body instanceof FormData)) {
        headers['Content-Type'] = 'application/json';
    }

    const csrftoken = getCookie('csrftoken');
    if (csrftoken) headers['X-CSRFToken'] = csrftoken;

    if (token) headers['Authorization'] = `Bearer ${token}`;

    const fetchOptions = {
        ...options,
        headers: headers
    };

    console.log(`[authFetch] ${method} ${url}`, headers);

    let res = await fetch(url, fetchOptions);

    if (res.status === 401) {
        if (!window.location.pathname.endsWith('/') && !window.location.pathname.includes('login')) {
            alert("Session expired. Please login again.");
            localStorage.clear();
            window.location.href = '/logout/';
        }
    }
    return res;
}

async function loadDashboard() {
    // Determine stats from API
    try {
        const totalEmpEl = document.getElementById('totalEmployees');
        if (!totalEmpEl) return; // Not on dashboard page

        const res = await authFetch(`${API_BASE}/employees/`);
        const data = await res.json();

        let count = 0;
        if (data.count !== undefined) count = data.count;
        else if (Array.isArray(data)) count = data.length;
        else if (data.results && Array.isArray(data.results)) count = data.results.length;

        totalEmpEl.innerText = count;
    } catch (e) {
        console.error("Dashboard Load Error:", e);
    }
}

async function loadEmployees() {
    const tbody = document.querySelector('#employeesTable tbody');
    if (!tbody) return; // Not on employees page

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
    if (!tbody) return; // Not on payroll page

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
// --- Global UI Persistence & Notification ---

// Safely preserve native functions for fallbacks
const nativeAlert = window.alert;
const nativeConfirm = window.confirm;

window.showToast = function (message, type = 'info') {
    const container = document.getElementById('toast-container');
    if (!container) {
        console.log("Toast Fallback:", message);
        return;
    }

    const toast = document.createElement('div');
    toast.className = `premium-toast ${type}`;

    let icon = '<i class="fas fa-info-circle" style="color:#3b82f6; font-size: 1.25rem;"></i>';
    if (type === 'success') icon = '<i class="fas fa-check-circle" style="color:#22c55e; font-size: 1.25rem;"></i>';
    if (type === 'error') icon = '<i class="fas fa-exclamation-circle" style="color:#ef4444; font-size: 1.25rem;"></i>';

    toast.innerHTML = `${icon}<span style="font-weight: 600; color: #1e293b; font-size: 0.95rem;">${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'toastOut 0.4s ease-in forwards';
        setTimeout(() => toast.remove(), 400);
    }, 4500);
};

// Override standard alert with Premium Toast
window.alert = function (message) {
    if (typeof message !== 'string') {
        try { message = JSON.stringify(message); } catch (e) { message = String(message); }
    }
    const lowerMsg = message.toLowerCase();
    const isError = lowerMsg.includes('fail') || lowerMsg.includes('error') || lowerMsg.includes('invalid') || lowerMsg.includes('wrong');
    const isSuccess = lowerMsg.includes('success') || lowerMsg.includes('saved') || lowerMsg.includes('complete') || lowerMsg.includes('updated');
    const type = isSuccess ? 'success' : (isError ? 'error' : 'info');
    showToast(message, type);
};

// Global Confirmation Logic
let globalConfirmResolve = null;

window.confirm = function (message, title = "Confirm Action", options = {}) {
    const modal = document.getElementById('globalCustomConfirm');
    if (!modal) {
        return nativeConfirm(message); // Fallback to native if modal structure missing
    }

    // Handle legacy customConfirm calls where 3rd param might be isDanger (boolean)
    let isDanger = false;
    let customIcon = null;

    if (typeof options === 'boolean') {
        isDanger = options;
    } else if (options) {
        isDanger = !!options.isDanger;
        customIcon = options.icon || null;
    }

    const titleEl = document.getElementById('globalConfirmTitle');
    const msgEl = document.getElementById('globalConfirmMessage');
    const yesBtn = document.getElementById('btnGlobalConfirmYes');
    const iconDiv = document.getElementById('globalConfirmIcon');

    titleEl.textContent = title;
    msgEl.textContent = message;

    // Auto-detect danger from keywords if not explicitly set
    if (!isDanger) {
        const lowerMsg = message.toLowerCase();
        isDanger = lowerMsg.includes('delete') || lowerMsg.includes('remove') || lowerMsg.includes('reject');
    }

    if (isDanger) {
        yesBtn.style.background = 'linear-gradient(135deg, #ef4444 0%, #b91c1c 100%)';
        yesBtn.style.boxShadow = '0 10px 25px -5px rgba(239, 68, 68, 0.4)';
        yesBtn.textContent = 'Yes, Proceed';
        if (message.toLowerCase().includes('delete')) yesBtn.textContent = 'Yes, Delete';
        if (message.toLowerCase().includes('reject')) yesBtn.textContent = 'Yes, Reject';

        iconDiv.innerHTML = '<i class="fas fa-exclamation-triangle" style="color: #ef4444;"></i>';
        iconDiv.style.background = 'rgba(239, 68, 68, 0.1)';
    } else {
        yesBtn.style.background = 'linear-gradient(135deg, #2563eb 0%, #1e40af 100%)';
        yesBtn.style.boxShadow = '0 10px 25px -5px rgba(37, 99, 235, 0.4)';
        yesBtn.textContent = 'Yes, Proceed';

        if (customIcon) {
            iconDiv.innerHTML = `<i class="${customIcon}" style="color: #ffffff;"></i>`;
            iconDiv.style.background = 'linear-gradient(135deg, rgba(255,255,255,0.1), rgba(255,255,255,0.05))';
            iconDiv.style.borderColor = 'rgba(255,255,255,0.2)';
        } else {
            iconDiv.innerHTML = '<i class="fas fa-question-circle" style="color: #3b82f6;"></i>';
            iconDiv.style.background = 'rgba(59, 130, 246, 0.1)';
        }
    }

    modal.classList.add('active');

    return new Promise((resolve) => {
        globalConfirmResolve = resolve;
    });
};

// Alias for older code
window.customConfirm = window.confirm;

// Handle Resolve/Reject for Global Confirm
document.addEventListener('click', (e) => {
    const cancelBtn = e.target.closest('#btnGlobalConfirmCancel');
    const yesBtn = e.target.closest('#btnGlobalConfirmYes');
    const modal = document.getElementById('globalCustomConfirm');

    if (cancelBtn) {
        modal.classList.remove('active');
        if (globalConfirmResolve) {
            globalConfirmResolve(false);
            globalConfirmResolve = null;
        }
    }

    if (yesBtn) {
        modal.classList.remove('active');
        if (globalConfirmResolve) {
            globalConfirmResolve(true);
            globalConfirmResolve = null;
        }
    }
});
