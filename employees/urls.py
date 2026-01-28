from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import EmployeeListCreateView, SalaryStructureViewSet, DepartmentViewSet, DesignationViewSet, EmployeeViewSet

router = DefaultRouter()
router.register(r"salary-structures", SalaryStructureViewSet, basename="salary-structure")
router.register(r"departments", DepartmentViewSet, basename="department")
router.register(r"designations", DesignationViewSet, basename="designation")
router.register(r"employees-api", EmployeeViewSet, basename="employee-api")

urlpatterns = [
    path("employees/", EmployeeListCreateView.as_view(), name="employee-list"),
    path("", include(router.urls)),
]
