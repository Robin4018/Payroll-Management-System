from django.db import models

class SalaryStructure(models.Model):
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2)
    hra = models.DecimalField(max_digits=10, decimal_places=2)
    allowances = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return str(self.basic_salary)
