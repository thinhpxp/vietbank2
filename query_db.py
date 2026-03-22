import os
import django
import sys

# Setup Django
sys.path.append(r'c:\Users\thinhpxp\Webapp_vietbank\ContractDraftingWebApp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ContractDraftingWebapp.settings')
django.setup()

from document_automation.models import MasterObject, LoanProfile, FieldValue

def test():
    with open(r'c:\Users\thinhpxp\query_result.txt', 'w', encoding='utf-8') as f:
        try:
            profile_id = 72
            contract_id = 2100 # Adjust if needed
            
            fvs = FieldValue.objects.filter(loan_profile_id=profile_id, master_object_id=contract_id)
            f.write(f"Profile {profile_id}, Object {contract_id} found {fvs.count()} values:\n")
            for fv in fvs:
                f.write(f"  - {fv.field.placeholder_key}: {fv.value}\n")
                
            fvs_master = FieldValue.objects.filter(loan_profile__isnull=True, master_object_id=contract_id)
            f.write(f"\nMaster Data for Object {contract_id} found {fvs_master.count()} values:\n")
            for fv in fvs_master:
                f.write(f"  - {fv.field.placeholder_key}: {fv.value}\n")
        except Exception as e:
            f.write(f"ERROR: {str(e)}\n")

if __name__ == "__main__":
    test()
