import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ContractDraftingWebApp.settings')
django.setup()

from document_automation.models import MasterObject, MasterObjectType

def check_objects():
    objects = MasterObject.objects.filter(deleted_at__isnull=True)[:50]
    print(f"{'ID':<5} | {'Type':<12} | {'Display Name':<40} | {'Identity Key':<15}")
    print("-" * 80)
    for obj in objects:
        ot = MasterObjectType.objects.filter(code=obj.object_type).first()
        id_key = ot.identity_field_key if ot else "N/A"
        print(f"{obj.id:<5} | {obj.object_type:<12} | {obj.display_name:<40} | {id_key:<15}")

if __name__ == "__main__":
    check_objects()
