from document_automation.models import MasterObject, User
from document_automation.views.master_views import MasterObjectViewSet
from rest_framework.request import Request
from rest_framework.test import APIRequestFactory

def run():
    print("--- DIAGNOSTIC START ---")
    try:
        user = User.objects.get(username='ROOT_TEST')
        print(f"User: {user.username}, is_superuser: {user.is_superuser}")
        
        p = MasterObject.objects.create(object_type='TEST')
        
        factory = APIRequestFactory()
        req = factory.post('/')
        req.user = user
        drf_req = Request(req)
        
        print(f"DRF Request User: {drf_req.user.username}, is_superuser: {drf_req.user.is_superuser}")
        
        viewset = MasterObjectViewSet()
        viewset.request = drf_req
        
        res = viewset.hard_delete(drf_req, pk=p.id)
        print(f"Result Status: {res.status_code}")
        if res.status_code != 200:
            print(f"Error Detail: {res.data}")
            
        p.delete() if MasterObject.objects.filter(pk=p.id).exists() else None
        
    except Exception as e:
        print(f"Error: {e}")
    print("--- DIAGNOSTIC END ---")

run()
