import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ContractDraftingWebApp.settings')
django.setup()

from document_automation.models import MasterObject, MasterObjectType

def verify_person_logic():
    print(f"{'Type':<10} | {'Identity Key':<15} | {'Display Name':<30} | {'Additional Info'}")
    print("-" * 100)
    
    # Check PERSON config
    cfg = MasterObjectType.objects.filter(code='PERSON').first()
    if cfg:
        print(f"Config: Identity={cfg.identity_field_key}, Template={cfg.dynamic_summary_template}")
    
    # Check objects
    from document_automation.serializers import MasterObjectSerializer
    
    persons = MasterObject.objects.filter(object_type='PERSON', deleted_at__isnull=True)[:5]
    for p in persons:
        serializer = MasterObjectSerializer(p)
        data = serializer.data
        print(f"{p.object_type:<10} | {cfg.identity_field_key:<15} | {data['display_name']:<30} | {data['additional_info']}")

if __name__ == "__main__":
    verify_person_logic()
