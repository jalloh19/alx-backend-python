#!/usr/bin/env python
"""Script to create test users"""

from chats.models import User

# Delete existing test users
User.objects.filter(username__in=['alice', 'bob']).delete()

# Create test users
users = [
    {
        'username': 'alice',
        'password': 'password123',
        'email': 'alice@example.com',
        'first_name': 'Alice',
        'last_name': 'Smith',
        'role': 'guest'
    },
    {
        'username': 'bob',
        'password': 'password123',
        'email': 'bob@example.com',
        'first_name': 'Bob',
        'last_name': 'Jones',
        'role': 'host'
    }
]

for user_data in users:
    User.objects.create_user(**user_data)
    print(f"✅ Created user: {user_data['username']}")

print("\n🎉 All test users created successfully!")
