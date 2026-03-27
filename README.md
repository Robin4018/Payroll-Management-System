# 🚀 Universal Payroll Management System

A high-performance, **Multi-tenant SaaS** payroll and HR management solution built with **Django**. Designed to handle complex organizational workflows for Schools, Colleges, and Corporate entities with absolute data isolation. I've Submitted this as my Final Year main Project. If you're interested in contributing to this project, kindly create a seperate new branch and feel free to work on this.  

---

## 🌟 Key Features

### 🏢 Multi-tenant Architecture
- **Data Isolation:** Securely manage multiple organizations (Tenants) within a single deployment.
- **Sector Support:** Tailored modules for **Schools**, **Colleges**, and **Companies**.

### 💸 Advanced Payroll Engine
- **Salary Automation:** Automated calculation of monthly payouts based on CTC structures.
- **Statutory Compliance:** Built-in logic for **PF (Provident Fund)**, **ESI**, **TDS**, and **Professional Tax**.
- **Component Management:** Dynamic handling of bonuses, overtime, and deductions.

### 👥 Employee Lifecycle Management
- **Smart Onboarding:** Automated employee code generation and profile management.
- **Document Vault:** Secure storage for employee ID proofs, educational certificates, and resumes.
- **Bank Integration:** Seamless management of employee bank details for direct payouts.

### 📅 Attendance & Leave Tracking
- **Real-time Monitoring:** Integration-ready for external attendance APIs.
- **Leave Workflows:** Comprehensive leave application and approval logic with balance tracking.

### 📊 Powerful Analytics
- **Dynamic Dashboards:** Real-time stats on employee counts, active status, and departmental distributions.
- **Reporting:** Exportable reports for payroll audits and financial planning.

---

## 🛠️ Technology Stack

- **Backend:** Python 3.12+, Django 5.x
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla), Django Templates
- **Database:** SQLite (Development), PostgreSQL (Production-ready)
- **Infrastructure:** Docker, Docker-Compose
- **Tools:** Git, REST APIs, Virtualenv

---

## 🚀 Getting Started

### Prerequisites
- Python 3.12 or higher
- Git

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Robin4018/Payroll-Management-System.git
   cd Payroll-Management-System
   ```

2. **Set up the virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations:**
   ```bash
   python manage.py migrate
   ```

5. **Start the server:**
   ```bash
   python manage.py runserver
   ```

---

## 📁 Project Structure

```text
├── employees/      # Employee profile and document management
├── payroll/        # Salary processing and statutory logic
├── tenants/        # Multi-tenant organization handling
├── attendance/     # Attendance tracking and API integrations
├── frontend/       # Responsive UI templates and assets
├── backend/        # Core business logic and settings
└── manage.py       # Django management script
```

---
*Developed with by [Robin](https://github.com/Robin4018)*
