from django.db import models
from tenants.models import Tenant
from django.contrib.auth.models import User


class Department(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='departments')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Designation(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, related_name='designations')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='designations')
    name = models.CharField(max_length=100)
    rank = models.IntegerField(default=0, help_text="Higher value means higher rank")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.department.name if self.department else 'Global'})"

class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    tenant = models.ForeignKey(
        Tenant,
        on_delete=models.CASCADE,
        related_name="employees"
    )

    employee_code = models.CharField(max_length=50, null=True, blank=True)
    
    # -- Employment Details --
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
    secondary_departments = models.ManyToManyField(Department, blank=True, related_name='secondary_employees')
    designation_fk = models.ForeignKey(Designation, on_delete=models.SET_NULL, null=True, blank=True, related_name='employees')
    # Deprecated fallback field, keep for migration safety till fully removed
    designation = models.CharField(max_length=100, null=True, blank=True) 
    
    reporting_manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinates')
    work_location = models.CharField(max_length=100, default='Main Campus')
    
    class EmploymentType(models.TextChoices):
        PERMANENT = 'PERMANENT', 'Permanent'
        CONTRACT = 'CONTRACT', 'Contract'
        GUEST = 'GUEST_LECTURER', 'Guest Lecturer'
        INTERN = 'INTERN', 'Intern'

    employment_type = models.CharField(
        max_length=20,
        choices=EmploymentType.choices,
        default=EmploymentType.PERMANENT
    )

    # -- Personal Details --
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    
    # Financial Info
    ctc = models.DecimalField(max_digits=12, decimal_places=2, help_text="Annual Cost to Company", default=0.00)
    qualification = models.CharField(max_length=255, null=True, blank=True)
    
    date_of_joining = models.DateField()
    date_of_birth = models.DateField(null=True, blank=True)
    
    class Gender(models.TextChoices):
        MALE = 'MALE', 'Male'
        FEMALE = 'FEMALE', 'Female'
        OTHER = 'OTHER', 'Other'
        
    gender = models.CharField(max_length=10, choices=Gender.choices, null=True, blank=True)
    blood_group = models.CharField(max_length=5, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    profile_photo = models.ImageField(upload_to='employee_photos/', null=True, blank=True)
    
    # -- Emergency Contact --
    emergency_contact_name = models.CharField(max_length=100, null=True, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, null=True, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.employee_code:
            # Generate ID: EMP + 0000 + ID
            # Robust way: Use tenant-specific sequence
            last_emp = Employee.objects.filter(tenant=self.tenant).order_by('id').last()
            if last_emp and last_emp.employee_code and last_emp.employee_code.startswith('EMP'):
                try:
                    # Try to extract number
                    last_num = int(last_emp.employee_code.replace('EMP', ''))
                    new_num = last_num + 1
                except:
                    # Fallback if manual codes broke the sequence
                    new_num = Employee.objects.filter(tenant=self.tenant).count() + 1
            else:
                 new_num = Employee.objects.filter(tenant=self.tenant).count() + 1
            
            self.employee_code = f"EMP{new_num:04d}"
            
            # Ensure uniqueness loop within tenant
            while Employee.objects.filter(employee_code=self.employee_code, tenant=self.tenant).exists():
                new_num += 1
                self.employee_code = f"EMP{new_num:04d}"

        super().save(*args, **kwargs)

    class Meta:
        unique_together = ('tenant', 'employee_code')

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.employee_code})"

class EmployeeBankDetails(models.Model):
    employee = models.OneToOneField(Employee, on_delete=models.CASCADE, related_name='bank_details')
    
    # Bank Info
    account_number = models.CharField(max_length=50)
    bank_name = models.CharField(max_length=100)
    ifsc_code = models.CharField(max_length=20)
    branch_name = models.CharField(max_length=100, blank=True)
    account_holder_name = models.CharField(max_length=100)
    
    # Statutory Info
    pan_number = models.CharField(max_length=20, null=True, blank=True)
    pf_account_number = models.CharField(max_length=50, null=True, blank=True)
    esi_number = models.CharField(max_length=50, null=True, blank=True)
    uan_number = models.CharField(max_length=50, null=True, blank=True) # Universal Account Number for PF

    def __str__(self):
        return f"{self.bank_name} - {self.account_number}"

class EmployeeDocument(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=100)
    document_type = models.CharField(max_length=50, choices=[
        ('RESUME', 'Resume/CV'),
        ('ID_PROOF', 'ID Proof'),
        ('ADDRESS_PROOF', 'Address Proof'),
        ('EDUCATION', 'Educational Certificate'),
        ('OTHER', 'Other')
    ], default='OTHER')
    file = models.FileField(upload_to='employee_docs/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.title} - {self.employee.first_name}"

class UserProfile(models.Model):
    class OrganizationType(models.TextChoices):
        SCHOOL = 'SCHOOL', 'School'
        COLLEGE = 'COLLEGE', 'College'
        COMPANY = 'COMPANY', 'Company'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    organization_type = models.CharField(max_length=20, choices=OrganizationType.choices)
    organization_name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.organization_type}"