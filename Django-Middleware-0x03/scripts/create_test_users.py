#!/usr/bin/env python
"""
Script to create test users for middleware testing
Run with: python manage.py shell < scripts/create_test_users.py
"""

from chats.models import User

print("Creating test users for middleware testing...")
print("=" * 50)

# Delete existing test users if they exist
users_to_delete = ['admin', 'moderator', 'guest']
deleted = User.objects.filter(username__in=users_to_delete).delete()
if deleted[0] > 0:
    print(f"Deleted {deleted[0]} existing test users")

# Create admin user
admin = User.objects.create_user(
    username='admin',
    password='admin123',
    email='admin@example.com',
    first_name='Admin',
    last_name='User',
    role='admin'
)
print(f"✅ Created admin user: {admin.username} (role: {admin.role})")

# Create moderator user
moderator = User.objects.create_user(
    username='moderator',
    password='mod123',
    email='moderator@example.com',
    first_name='Moderator',
    last_name='User',
    role='moderator'
)
print(f"✅ Created moderator user: {moderator.username} (role: {moderator.role})")

# Create guest user
guest = User.objects.create_user(
    username='guest',
    password='guest123',
    email='guest@example.com',
    first_name='Guest',
    last_name='User',
    role='guest'
)
print(f"✅ Created guest user: {guest.username} (role: {guest.role})")

print("=" * 50)
print("Test users created successfully!")
print("\nCredentials:")
print("  Admin:     username=admin,     password=admin123")
print("  Moderator: username=moderator, password=mod123")
print("  Guest:     username=guest,     password=guest123")
