from django.conf import settings
from rest_framework.test import APIClient
# from django.contrib.auth.models import User # Replaced
from django.contrib.auth import get_user_model
import pytest

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def authenticate(api_client):
    def do_authenticate(user=None, is_staff=False): # Added user=None
        if user is None:
            # Create a basic User instance if not provided.
            # This user won't be saved to DB unless explicitly done in the test.
            # For force_authenticate, an unsaved instance is usually fine.
            # If is_staff is True, create a staff user.
            user_kwargs = {'username': 'testdefaultuser', 'is_staff': is_staff}
            if is_staff:
                user_kwargs['email'] = 'staff_default@example.com' # Ensure unique email if saving
            else:
                user_kwargs['email'] = 'default_user@example.com' # Ensure unique email if saving
            
            # Check if user already exists if we were to save it, to avoid issues.
            # However, force_authenticate itself does not save.
            # The User() call here creates an in-memory instance.
            user = User(**user_kwargs) 
            # If the test requires a saved user, it should create it explicitly.
            # For example: User.objects.create_user(username='test', email='test@example.com', is_staff=is_staff)
            
        return api_client.force_authenticate(user=user)
    return do_authenticate
