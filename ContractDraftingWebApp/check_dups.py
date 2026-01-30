from document_automation.models import MasterObject, FieldValue
from collections import Counter

print("--- SYSTEM-WIDE REALESTATE IDENTIFIER CHECK ---")
mos = MasterObject.objects.filter(object_type='REALESTATE')
vals = []
for mo in mos:
    fvs = FieldValue.objects.filter(master_object=mo, field__placeholder_key='chung_nhan_qsdd', loan_profile__isnull=True)
    if fvs.exists():
        val = fvs.first().value.strip()
        vals.append(val)

counts = Counter(vals)
dups = {k: v for k, v in counts.items() if v > 1}
if dups:
    print(f"DUPLICATE IDENTIFIERS FOUND: {dups}")
else:
    print("No system-wide duplicate identifiers found for REALESTATE.")

# Check for Profile 30 specifically
print("\n--- PROFILE 30 SPECIFIC ANALYSIS ---")
from document_automation.models import LoanProfile, LoanProfileObjectLink
try:
    p = LoanProfile.objects.get(id=30)
    links = LoanProfileObjectLink.objects.filter(loan_profile=p, master_object__object_type='REALESTATE')
    print(f"Profile 30 currently has {links.count()} REALESTATE links.")
    for l in links:
        fv = FieldValue.objects.filter(master_object=l.master_object, field__placeholder_key='chung_nhan_qsdd', loan_profile__isnull=True).first()
        print(f" Link {l.id} -> Mo {l.master_object_id} (Val: {fv.value if fv else 'N/A'})")
except Exception as e:
    print(f"Error checking profile 30: {e}")
