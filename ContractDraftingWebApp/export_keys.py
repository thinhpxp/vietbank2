import os
import django
import sys

# Thiết lập encoding UTF-8 cho stdout
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ContractDraftingWebApp.settings')
django.setup()

from document_automation.models import Field

with open('keys_output.txt', 'w', encoding='utf-8') as f:
    f.write("AVAILABLE PLACEHOLDER KEYS\n")
    f.write("=" * 30 + "\n")
    f.write(f"{'ID':<5} | {'Label':<35} | {'Key':<25} | {'Group'}\n")
    f.write("-" * 85 + "\n")

    fields = Field.objects.all().select_related('group').order_by('group__order', 'order')
    for field in fields:
        group_name = field.group.name if field.group else "None"
        f.write(f"{field.id:<5} | {field.label:<35} | {field.placeholder_key:<25} | {group_name}\n")
