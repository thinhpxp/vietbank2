from django.utils import timezone
from document_automation.models import MasterObject, LoanProfile, LoanProfileObjectLink, User
from document_automation.views.master_views import MasterObjectViewSet
from rest_framework.test import APIRequestFactory
from rest_framework.request import Request
from rest_framework.exceptions import ValidationError
import sys

def run():
    print("--- STARTING VERIFICATION V2 ---")
    root = User.objects.get(username='ROOT_TEST')
    p = MasterObject.objects.create(object_type='PERSON')
    lp = LoanProfile.objects.create(name='Test Finalized', status='FINALIZED')
    LoanProfileObjectLink.objects.create(loan_profile=lp, master_object=p)
    
    factory = APIRequestFactory()
    request = factory.post('/') # Use POST for hard_delete
    request.user = root # Superuser!
    
    viewset = MasterObjectViewSet()
    viewset.request = Request(request)
    
    # Test Phase 7
    print("Testing Phase 7 (Dependency Guard)...")
    try:
        viewset.perform_destroy(p)
        print("FAIL: Deletion should have been blocked")
    except ValidationError as e:
        print(f"SUCCESS: Deletion blocked: {str(e)}")
        
    # Test Phase 8
    print("Testing Phase 8 (Hard Delete)...")
    # We must pass the request object to hard_delete
    res = viewset.hard_delete(viewset.request, pk=p.id)
    if res.status_code == 200:
        exists = MasterObject.objects.filter(pk=p.id).exists()
        print(f"SUCCESS: Hard delete works, exists in DB: {exists}")
    else:
        print(f"FAIL: Hard delete failed with status {res.status_code}: {res.data}")
    
    # Cleanup
    lp.delete()
    root.delete() 
    print("--- VERIFICATION COMPLETE ---")

run()
