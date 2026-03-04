
import os
import django
import sys

# Setup Django environment
sys.path.append(r'c:\Users\thinhpxp\Webapp_vietbank\ContractDraftingWebApp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ContractDraftingWebApp.settings')
django.setup()

from document_automation.models import MasterObject, AuditLog, AdminNotification, LoanProfile
from django.utils import timezone

def perform_cleanup():
    print("--- STARTING TOTAL DATABASE CLEANUP ---")
    
    # 1. Delete ALL MasterObjects
    # Cascade will handle FieldValue (of objects), MasterObjectRelation, LoanProfileObjectLink
    mo_count = MasterObject.objects.count()
    print(f"Deleting ALL {mo_count} MasterObjects...")
    MasterObject.objects.all().delete()
    print("Done.")

    # 2. Delete ALL LoanProfiles
    lp_count = LoanProfile.objects.count()
    print(f"Deleting ALL {lp_count} LoanProfiles...")
    LoanProfile.objects.all().delete()
    print("Done.")

    # 3. Clear Audit Logs (if any new ones)
    audit_count = AuditLog.objects.count()
    print(f"Clearing {audit_count} AuditLogs...")
    AuditLog.objects.all().delete()
    print("Done.")

    # 4. Delete Expired Notifications
    expired_notifs = AdminNotification.objects.filter(expires_at__lt=timezone.now())
    notif_count = expired_notifs.count()
    print(f"Deleting {notif_count} expired AdminNotifications...")
    expired_notifs.delete()
    print("Done.")

    print("--- TOTAL CLEANUP COMPLETED SUCCESSFULLY ---")

if __name__ == "__main__":
    try:
        perform_cleanup()
    except Exception as e:
        print(f"CRITICAL ERROR DURING CLEANUP: {e}")
