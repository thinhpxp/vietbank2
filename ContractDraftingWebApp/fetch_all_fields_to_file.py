import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ContractDraftingWebApp.settings')
django.setup()

from document_automation.models import Field, FieldGroup

data = {
    "groups": []
}

for group in FieldGroup.objects.all().order_by('order'):
    group_info = {
        "name": group.name,
        "slug": group.slug,
        "entity_type": group.entity_type,
        "allowed_object_types": list(group.allowed_object_types.values_list('code', flat=True)),
        "fields": []
    }
    
    for f in Field.objects.filter(group=group).order_by('order'):
        group_info["fields"].append({
            "label": f.label,
            "key": f.placeholder_key,
            "data_type": f.data_type,
            "note": f.note
        })
    
    data["groups"].append(group_info)

with open('fields_dump.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=4, ensure_ascii=False)

print("Done writing to fields_dump.json")
