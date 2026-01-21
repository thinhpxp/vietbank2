import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ContractDraftingWebApp.settings')
django.setup()

from document_automation.models import Field, FieldGroup, FormView, MasterObjectType

print("--- EXAMINING KHOAN VAY GROUP ---")
group = FieldGroup.objects.filter(slug='tt-khoan-vay').first()
if group:
    print(f"Group: {group.name} (ID: {group.id})")
    print(f"Slug: {group.slug}")
    print(f"Allowed Object Types: {list(group.allowed_object_types.values_list('code', flat=True))}")
    print(f"Allowed Forms: {list(group.allowed_forms.values_list('slug', flat=True))}")
    
    fields = Field.objects.filter(group=group)
    print(f"Fields count: {fields.count()}")
    for f in fields:
        print(f"  - Field: {f.label} ({f.placeholder_key}) | Active: {f.is_active} | Forms: {list(f.allowed_forms.values_list('slug', flat=True))}")
else:
    print("Group 'tt-khoan-vay' not found!")

print("\n--- EXAMINING FORM VIEWS ---")
for fv in FormView.objects.all():
    print(f"Form: {fv.name} ({fv.slug})")

print("\n--- EXAMINING OBJECT TYPES ---")
for ot in MasterObjectType.objects.all():
    print(f"Type: {ot.name} ({ot.code})")
