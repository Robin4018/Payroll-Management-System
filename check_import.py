
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

try:
    from payroll.views import ReportViewSet
    print("ReportViewSet imported successfully")
except Exception as e:
    import traceback
    print(traceback.format_exc())
