import os
import django
import sys

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ContractDraftingWebApp.settings')
django.setup()

from document_automation.models import MasterObjectType, MasterSection, MasterField, Role, GeneralField

print("# MASTER OBJECT TYPES")
for ot in MasterObjectType.objects.all():
    print(f"- {ot.code} ({ot.name}) - Display: {ot.form_display_mode}")

print("\n# SECTIONS AND FIELDS")
for ot in MasterObjectType.objects.all():
    print(f"\n## {ot.name} ({ot.code})")
    sections = MasterSection.objects.filter(object_type=ot).order_by('order')
    for sec in sections:
        print(f"### Section: {sec.name}")
        fields = MasterField.objects.filter(section=sec).order_by('order')
        for f in fields:
            print(f"| {f.placeholder_key} | {f.label} | {f.description or ''} |")

print("\n# ROLES")
for r in Role.objects.all():
    print(f"- {r.name} (Slug: {r.slug})")

print("\n# GENERAL FIELDS")
for gf in GeneralField.objects.all():
    print(f"| {gf.placeholder_key} | {gf.label} |")
