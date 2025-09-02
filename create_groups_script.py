#!/usr/bin/env python
"""
Script to create all required user groups for the OMS application.
This can be run in Django shell or as a standalone script.

Usage in Django shell:
python manage.py shell
>>> exec(open('create_groups_script.py').read())

Or run directly:
python create_groups_script.py
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'oms.settings')
django.setup()

from django.contrib.auth.models import Group

def create_groups():
    """Create all required user groups for the OMS application."""
    
    # List of all groups that need to be created
    groups = [
        'AM',
        'AM_D', 
        'AM_M',
        'EMP',
        'EMP_D',
        'EMP_M',
        'EV',
        'EV_D',
        'EV_M'
    ]
    
    created_count = 0
    existing_count = 0
    
    print("Creating user groups for OMS application...")
    print("=" * 50)
    
    for group_name in groups:
        group, created = Group.objects.get_or_create(name=group_name)
        if created:
            print(f"✅ Successfully created group: {group_name}")
            created_count += 1
        else:
            print(f"⚠️  Group already exists: {group_name}")
            existing_count += 1
    
    # Summary
    print("=" * 50)
    print(f"Summary:")
    print(f"- Created: {created_count} groups")
    print(f"- Already existed: {existing_count} groups")
    print(f"- Total groups: {len(groups)}")
    
    if created_count > 0:
        print(f"\n🎉 Successfully created {created_count} new groups!")
    else:
        print(f"\n📋 All groups already exist in the database.")

if __name__ == "__main__":
    create_groups()
