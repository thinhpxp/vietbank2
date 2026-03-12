import os
import django
import sys

# Thiết lập môi trường Django
# Điều chỉnh path nếu cần thiết
sys.path.append('c:/Users/thinhpxp/Webapp_vietbank/ContractDraftingWebApp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ContractDraftingWebApp.settings')
django.setup()

from document_automation.models import MasterObject, AuditLog, Field, FieldValue
from document_automation.services.loan_service import LoanService
from document_automation.views.system_views import format_changes
from django.contrib.auth.models import User

def verify_audit_log():
    user = User.objects.filter(is_superuser=True).first()
    if not user:
        print("Không tìm thấy superuser để test.")
        return

    print(f"--- Bắt đầu kiểm tra Audit Log chi tiết ---")
    
    # 1. Test MasterObject UPDATE
    master = MasterObject.objects.filter(deleted_at__isnull=True).first()
    if master:
        print(f"Testing MasterObject ID: {master.id}")
        # Giả lập lấp đầy field_values
        fvs = FieldValue.objects.filter(master_object=master, loan_profile__isnull=True)
        field_values = {fv.field.placeholder_key: fv.value for fv in fvs}
        
        # Thay đổi một giá trị
        if field_values:
            first_key = list(field_values.keys())[0]
            old_val = field_values[first_key]
            field_values[first_key] = "VERIFY_TEST_VALUE"
            
            print(f"Thay đổi {first_key}: {old_val} -> VERIFY_TEST_VALUE")
            
            # Chúng ta không gọi ViewSet trực tiếp mà có thể mock hoặc kiểm tra hàm format_changes
            from document_automation.views.system_views import format_changes
            changed = {first_key: {"from": old_val, "to": "VERIFY_TEST_VALUE"}}
            formatted = format_changes(changed)
            print(f"Kết quả format_changes: {formatted}")
            
            if "->" in formatted:
                print("✅ format_changes hoạt động tốt.")
            else:
                print("❌ format_changes không định dạng đúng.")
        else:
            print("MasterObject không có field_values để test.")
    
    # 2. Kiểm tra log gần nhất trong DB
    latest_log = AuditLog.objects.order_by('-timestamp').first()
    if latest_log:
        print(f"Log gần nhất: Action={latest_log.action}, Target={latest_log.target_model}")
        print(f"Details: {latest_log.details}")
    
    print("--- Kết thúc kiểm tra ---")

if __name__ == "__main__":
    verify_audit_log()
