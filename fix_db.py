import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

with connection.cursor() as cursor:
    try:
        cursor.execute("ALTER TABLE django_content_type ADD COLUMN name VARCHAR(100) AFTER model;")
        print("Successfully added 'name' column to 'django_content_type'.")
    except Exception as e:
        print(f"Error: {e}")
