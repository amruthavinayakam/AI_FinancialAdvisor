#!/usr/bin/env python3
"""
Fixed database setup script for Financial Advisor AI Agent
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.append(str(project_root))
sys.path.append(str(project_root / "backend" / "django_app"))

# Django setup
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')

import django
django.setup()

from django.core.management import execute_from_command_line

def run_django_migrations():
    """Run Django migrations"""
    try:
        print("Running Django migrations...")
        
        # Make migrations
        execute_from_command_line(['manage.py', 'makemigrations', 'core'])
        print("✅ Django migrations created")
        
        # Apply migrations
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Django migrations applied")
        
    except Exception as e:
        print(f"❌ Error running migrations: {e}")
        raise

def main():
    """Main setup function"""
    print("🚀 Setting up Financial Advisor AI Agent Database...")
    print("=" * 60)
    
    try:
        # Run Django migrations
        print("\n1. Running Django migrations...")
        run_django_migrations()
        
        print("\n" + "=" * 60)
        print("✅ Database setup completed successfully!")
        print("\nNext steps:")
        print("1. Test your connection: python test_database.py")
        print("2. Start the FastAPI server: python -m backend.fastapi_app.main")
        print("3. Start the Django server: python backend/django_app/manage.py runserver")
        
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
