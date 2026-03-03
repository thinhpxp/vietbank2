
import os
import django
from django.utils import timezone
from rest_framework.test import APIRequestFactory, force_authenticate
from django.contrib.auth.models import User

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ContractDraftingWebApp.settings')
django.setup()

from document_automation.models import LoanProfile, MasterObject
from document_automation.views import LoanProfileViewSet

def simulate_auto_save():
    try:
        profile = LoanProfile.objects.get(id=68)
        user = User.objects.get(username='admin')
        
        factory = APIRequestFactory()
        view = LoanProfileViewSet.as_view({'post': 'save_form_data'})
        
        # Payload with a NEW person (partial data)
        payload = {
            "is_auto_save": True,
            "object_sections": {
                "PERSON": [
                    {
                        "roles": ["NGUOI_VAY"],
                        "individual_field_values": {
                            "ho_ten": "Test Auto Save Draft",
                            "cccd_so": "999888777"
                        }
                    }
                ]
            }
        }
        
        request = factory.post('/api/loan-profiles/68/save_form_data/', payload, format='json')
        force_authenticate(request, user=user)
        
        response = view(request, pk=68)
        print(f"Response Status: {response.status_code}")
        
        # Check if a new MasterObject was created and if it is a draft
        latest_obj = MasterObject.objects.latest('id')
        print(f"Latest MasterObject ID: {latest_obj.id}")
        print(f"Name: {latest_obj.display_name}")
        print(f"IsDraft: {latest_obj.is_draft}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    simulate_auto_save()
