from document_automation.models import LoanProfile, LoanProfileObjectLink, FieldValue, MasterObject
print("--- PROFILE 30 REALESTATE LINKS ---")
p = LoanProfile.objects.get(id=30)
links = LoanProfileObjectLink.objects.filter(loan_profile=p, master_object__object_type='REALESTATE')
for l in links:
    mo = l.master_object
    fvs = FieldValue.objects.filter(master_object=mo, field__placeholder_key='chung_nhan_qsdd', loan_profile__isnull=True)
    val = fvs.first().value if fvs.exists() else "N/A"
    print(f'Link ID: {l.id}, Master ID: {mo.id}, Identity: {val}')

print("\n--- ALL REALESTATE MASTER OBJECTS ---")
mos = MasterObject.objects.filter(object_type='REALESTATE').order_by('-id')
for mo in mos:
    fvs = FieldValue.objects.filter(master_object=mo, field__placeholder_key='chung_nhan_qsdd', loan_profile__isnull=True)
    val = fvs.first().value if fvs.exists() else "N/A"
    print(f'M_ID: {mo.id}, Identity: {val}')
