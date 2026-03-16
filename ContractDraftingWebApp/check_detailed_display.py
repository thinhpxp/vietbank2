import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ContractDraftingWebApp.settings')
django.setup()

from document_automation.models import MasterObject, MasterObjectType, FieldValue

def check_objects():
    types_to_check = ['ATTORNEY', 'PERSON', 'VEHICLE', 'BRANCH']
    print(f"{'Type':<12} | {'Identity Key':<15} | {'Display Name':<45}")
    print("-" * 80)
    
    for t_code in types_to_check:
        obj = MasterObject.objects.filter(object_type=t_code, deleted_at__isnull=True).first()
        if not obj:
            continue
            
        ot = MasterObjectType.objects.filter(code=t_code).first()
        id_key = ot.identity_field_key if ot else "N/A"
        
        # Check if it has name_keys values
        name_keys = ['ho_ten', 'nguoi_dai_dien', 'ten_tai_san', 'ten_doi_tuong', 'ten_khach_hang', 'name', 'full_name']
        name_fvs = FieldValue.objects.filter(
            master_object=obj, 
            field__placeholder_key__in=name_keys,
            loan_profile__isnull=True
        )
        has_name = name_fvs.exists()
        
        print(f"{t_code:<12} | {id_key:<15} | {obj.display_name:<45}")
        if has_name:
            for nfv in name_fvs:
                print(f"  - Name Field: {nfv.field.placeholder_key} = {nfv.value}")
        
        if id_key != "N/A":
            id_fv = FieldValue.objects.filter(
                master_object=obj,
                field__placeholder_key=id_key,
                loan_profile__isnull=True
            ).first()
            if id_fv:
                print(f"  - Id Field: {id_key} = {id_fv.value}")

if __name__ == "__main__":
    check_objects()
