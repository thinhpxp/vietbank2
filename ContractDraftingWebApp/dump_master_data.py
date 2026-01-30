import os
import django
import sys
import io

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ContractDraftingWebApp.settings')
django.setup()

from document_automation.models import MasterObjectType, FieldGroup, Field, Role

output = io.StringIO()

def log(msg):
    output.write(msg + "\n")

log("# MASTER OBJECT TYPES")
for ot in MasterObjectType.objects.all():
    log(f"- {ot.code} ({ot.name}) - Display: {ot.form_display_mode}")

log("\n# SECTIONS AND FIELDS")
# Groups by Category
for entity_val, entity_name in FieldGroup.ENTITY_CHOICES:
    log(f"\n## Entity: {entity_name} ({entity_val})")
    groups = FieldGroup.objects.filter(entity_type=entity_val).order_by('order')
    for g in groups:
        log(f"### Group: {g.name}")
        fields = Field.objects.filter(group=g).order_by('order')
        for f in fields:
            ot_target = getattr(f, 'object_type_target', '')
            log(f"| {f.placeholder_key} | {f.label} | {ot_target or 'ALL'} |")

log("\n# FIELDS WITHOUT GROUPS (CORE?)")
core_fields = Field.objects.filter(group__isnull=True)
for f in core_fields:
    log(f"| {f.placeholder_key} | {f.label} |")

log("\n# ROLES")
for r in Role.objects.all():
    log(f"- {r.name} (Slug: {r.slug or 'N/A'})")

with open('data_dump.txt', 'w', encoding='utf-8') as f:
    f.write(output.getvalue())
print("Saved to data_dump.txt")
