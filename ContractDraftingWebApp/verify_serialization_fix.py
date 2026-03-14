import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ContractDraftingWebApp.settings')
django.setup()

from django.contrib.auth.models import User
from document_automation.serializers import UserSerializer

def verify():
    # Tìm user có chi nhánh
    user = User.objects.filter(profile__branch__isnull=False).first()
    if not user:
        print("No user with branch found in DB.")
        return

    print(f"User found: {user.username}")
    print(f"Branch ID in Profile (via DB): {user.profile.branch_id}")

    # Serialize using UserSerializer
    serializer = UserSerializer(user)
    data = serializer.data
    
    serialized_branch_id = data.get('branch_id')
    serialized_branch_name = data.get('branch_name')
    
    print(f"Serialized branch_id: {serialized_branch_id}")
    print(f"Serialized branch_name: {serialized_branch_name}")
    
    if serialized_branch_id == user.profile.branch_id:
        print("SUCCESS: branch_id matches DB.")
    else:
        print(f"FAILURE: branch_id ({serialized_branch_id}) mismatch with DB ({user.profile.branch_id}).")

if __name__ == '__main__':
    verify()
