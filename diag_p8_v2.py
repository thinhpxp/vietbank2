from document_automation.models import MasterObject, User
from document_automation.views.master_views import MasterObjectViewSet
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

def run():
    print("--- DIAGNOSTIC V2 START ---")
    try:
        # Create user inside script to avoid session/process issues
        User.objects.filter(username='ROOT_TEST').delete()
        user = User.objects.create_superuser('ROOT_TEST', 'root@test.com', 'Admin@123456')
        print(f"Created User: {user.username}, is_superuser: {user.is_superuser}")
        
        p = MasterObject.objects.create(object_type='TEST')
        p_id = p.id
        print(f"Created Test Object ID: {p_id}")
        
        factory = APIRequestFactory()
        req = factory.post(f'/api/master-objects/{p_id}/hard_delete/')
        req.user = user
        drf_req = Request(req)
        
        print(f"DRF Request User: {drf_req.user.username}, is_superuser: {drf_req.user.is_superuser}")
        
        viewset = MasterObjectViewSet()
        viewset.request = drf_req
        
        # Simulating the action call
        res = viewset.hard_delete(drf_req, pk=p_id)
        print(f"Result Status: {res.status_code}")
        if res.status_code != 200:
            print(f"Error Detail: {res.data}")
        else:
            exists = MasterObject.objects.filter(pk=p_id).exists()
            print(f"Hard delete verification: Exists in DB={exists} (Expected: False)")
            
        # Cleanup
        user.delete()
        if MasterObject.objects.filter(pk=p_id).exists():
             MasterObject.objects.filter(pk=p_id).delete()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    print("--- DIAGNOSTIC V2 END ---")

run()
