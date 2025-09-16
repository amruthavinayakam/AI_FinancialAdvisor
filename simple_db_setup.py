#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Simple database setup script for Financial Advisor AI Agent
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.django_app.core.settings')

import django
django.setup()

from django.core.management import execute_from_command_line

def run_django_migrations():
    """Run Django migrations"""
    try:
        print("Running Django migrations...")
        
        # Make migrations
        execute_from_command_line(['manage.py', 'makemigrations', 'core'])
        print("Django migrations created")
        
        # Apply migrations
        execute_from_command_line(['manage.py', 'migrate'])
        print("Django migrations applied")
        
    except Exception as e:
        print(f"Error running migrations: {e}")
        raise

def main():
    """Main setup function"""
    print("Setting up Financial Advisor AI Agent Database...")
    print("=" * 60)
    
    try:
        # Run Django migrations
        print("\n1. Running Django migrations...")
        run_django_migrations()
        
        print("\n" + "=" * 60)
        print("Database setup completed successfully!")
        print("\nNext steps:")
        print("1. Start the FastAPI server: python -m backend.fastapi_app.main")
        print("2. Start the Django server: python backend/django_app/manage.py runserver")
        print("3. Access Django admin at: http://localhost:8000/admin/")
        print("4. Access FastAPI docs at: http://localhost:8001/docs")
        
    except Exception as e:
        print(f"\nSetup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
