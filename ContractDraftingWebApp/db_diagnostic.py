
import os
import django
import sys

# Setup Django environment
sys.path.append(r'c:\Users\thinhpxp\Webapp_vietbank\ContractDraftingWebApp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ContractDraftingWebApp.settings')
django.setup()

from document_automation.models import MasterObject, LoanProfile, FieldValue, AuditLog, LoanProfileObjectLink, AdminNotification
from django.db.models import Count
from django.utils import timezone

def get_stats():
    stats = {}
    
    # 1. MasterObjects (Soft Deleted or Drafts)
    stats['deleted_master_objects'] = MasterObject.objects.filter(deleted_at__isnull=False).count()
    stats['draft_master_objects'] = MasterObject.objects.filter(is_draft=True).count()
    stats['active_master_objects'] = MasterObject.objects.filter(deleted_at__isnull=True, is_draft=False).count()
    
    # 2. LoanProfiles
    stats['total_loan_profiles'] = LoanProfile.objects.count()
    stats['default_named_profiles'] = LoanProfile.objects.filter(name="Hồ sơ mới").count()
    # Profiles with no linked objects or values
    stats['empty_profiles'] = LoanProfile.objects.annotate(
        num_links=Count('object_links'),
        num_values=Count('fieldvalue')
    ).filter(num_links=0, num_values=0).count()
    
    # 3. FieldValues
    stats['total_field_values'] = FieldValue.objects.count()
    # Orphaned values (though cascade usually handles this, good to check)
    stats['orphaned_field_values'] = FieldValue.objects.filter(loan_profile__isnull=True, master_object__isnull=True).count()
    
    # 4. AuditLogs
    stats['total_audit_logs'] = AuditLog.objects.count()
    
    # 5. Notifications
    stats['expired_notifications'] = AdminNotification.objects.filter(expires_at__lt=timezone.now()).count()
    
    return stats

if __name__ == "__main__":
    try:
        results = get_stats()
        print("--- DATABASE DIAGNOSTIC RESULTS ---")
        for key, value in results.items():
            print(f"{key}: {value}")
    except Exception as e:
        print(f"Error: {e}")
