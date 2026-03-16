import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ContractDraftingWebApp.settings')
django.setup()

from document_automation.models import MasterObjectType

def check_configs():
    configs = MasterObjectType.objects.all()
    print(f"{'Code':<25} | {'Identity Key':<20} | {'Summary Template'}")
    print("-" * 80)
    for cfg in configs:
        print(f"{cfg.code:<25} | {cfg.identity_field_key or 'None':<20} | {cfg.dynamic_summary_template or 'None'}")

if __name__ == "__main__":
    check_configs()
