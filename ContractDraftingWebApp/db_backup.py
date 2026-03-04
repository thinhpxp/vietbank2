
import os
import django
import sys
from django.core.management import call_command
import json

# Setup Django environment
sys.path.append(r'c:\Users\thinhpxp\Webapp_vietbank\ContractDraftingWebApp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ContractDraftingWebApp.settings')
django.setup()

def perform_backup():
    backup_dir = 'backup_cleanup_20260304'
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    backup_path = os.path.join(backup_dir, 'db_backup.json')
    print(f"Starting backup to {backup_path}...")
    
    with open(backup_path, 'w', encoding='utf-8') as f:
        call_command('dumpdata', exclude=['auth.permission', 'contenttypes'], stdout=f)
    
    print("Backup completed successfully.")

if __name__ == "__main__":
    try:
        perform_backup()
    except Exception as e:
        print(f"Error during backup: {e}")
