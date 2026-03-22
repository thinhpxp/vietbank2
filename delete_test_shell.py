from django.utils import timezone
from document_automation.models import MasterObject, MasterObjectRelation, LoanProfile, LoanProfileObjectLink, User
from document_automation.serializers import MasterObjectSerializer
import traceback

def run_test():
    with open(r'c:\Users\thinhpxp\delete_test_result.txt', 'w', encoding='utf-8') as f:
        try:
            # 1. Setup Data
            p_type = 'PERSON'
            a_type = 'REALESTATE'
            root = User.objects.filter(is_superuser=True).first()
            
            p = MasterObject.objects.create(object_type=p_type)
            a = MasterObject.objects.create(object_type=a_type)
            rel = MasterObjectRelation.objects.create(source_object=a, target_object=p, relation_type='OWNER')
            
            f.write(f"Created Person {p.id} and Asset {a.id} with Relation {rel.id}\n")
            
            # --- PHASE 6: Soft Delete Consistency ---
            p.deleted_at = timezone.now()
            p.save()
            f.write(f"Soft-deleted Person {p.id}\n")
            
            # Check if relation is hidden in Asset serializer
            ser = MasterObjectSerializer(a)
            valid_rels = [r for r in a.relations_as_source.all() if ser._is_relation_valid(r)]
            f.write(f"Is relation to deleted person valid? {rel in valid_rels} (Expected: False)\n")
            
            # --- PHASE 7: Dependency Check ---
            lp = LoanProfile.objects.create(name="Test Finalized", status='FINALIZED')
            link = LoanProfileObjectLink.objects.create(loan_profile=lp, master_object=p)
            f.write(f"Linked deleted person to FINALIZED profile {lp.id}\n")
            
            # Try destroy (simulating perform_destroy)
            from rest_framework.exceptions import ValidationError
            from document_automation.views.master_views import MasterObjectViewSet
            from rest_framework.request import Request
            from rest_framework.test import APIRequestFactory
            
            factory = APIRequestFactory()
            request = factory.delete('/')
            request.user = root
            
            viewset = MasterObjectViewSet()
            viewset.request = Request(request)
            
            try:
                viewset.perform_destroy(p)
                f.write("ERROR: Deletion should have been blocked for FINALIZED profile but passed.\n")
            except ValidationError as e:
                f.write(f"Success: Deletion blocked as expected with message: {str(e)}\n")
            
            # --- PHASE 8: Hard Delete ---
            # Simulate hard_delete logic
            if root.is_superuser:
                # We query again because pk might have changed or to simulate fresh retrieval
                obj_to_purge = MasterObject.objects.filter(pk=p.id).first()
                if obj_to_purge:
                    obj_to_purge.delete()
                    exists = MasterObject.objects.filter(pk=p.id).exists()
                    f.write(f"Hard-delete executed. Exists in DB? {exists} (Expected: False)\n")
                else:
                    f.write("ERROR: Could not find object for hard deletion.\n")
            
            # Cleanup
            a.delete()
            lp.delete()
            
        except Exception as e:
            f.write(f"EXCEPTION: {str(e)}\n")
            f.write(traceback.format_exc())

run_test()
