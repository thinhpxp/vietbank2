
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ContractDraftingWebApp.settings')
django.setup()

from document_automation.models import MasterObject

def check_master_objects():
    print("Listing ALL MasterObjects (including drafts):")
    all_objs = MasterObject.objects.all().order_by('-id')[:10]
    for obj in all_objs:
        print(f"ID: {obj.id}, Type: {obj.object_type}, Name: {obj.display_name}, IsDraft: {getattr(obj, 'is_draft', 'N/A')}")

if __name__ == "__main__":
    check_master_objects()
