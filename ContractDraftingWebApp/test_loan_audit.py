import os
import django
import sys

# Thiết lập môi trường Django
sys.path.append('c:/Users/thinhpxp/Webapp_vietbank/ContractDraftingWebApp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ContractDraftingWebApp.settings')
django.setup()

from document_automation.models import LoanProfile, AuditLog, Field, FieldValue, MasterObject
from document_automation.services.loan_service import LoanService
from django.contrib.auth.models import User

def test_loan_logging():
    user = User.objects.filter(is_superuser=True).first()
    profile = LoanProfile.objects.all().first()
    
    if not profile or not user:
        print("Không có hồ sơ hoặc user để test.")
        return

    print(f"Testing Profile: {profile.name} (ID: {profile.id})")
    
    # 1. Chuẩn bị dữ liệu thay đổi
    # Lấy field chung bất kỳ
    fv = FieldValue.objects.filter(loan_profile=profile, master_object__isnull=True).first()
    if not fv:
        # Nếu chưa có, lấy đại một field
        field = Field.objects.all().first()
        if not field:
            print("Không có field nào trong hệ thống.")
            return
        key = field.placeholder_key
        old_val = "Initial"
    else:
        key = fv.field.placeholder_key
        old_val = fv.value

    new_val = f"Updated_at_{os.urandom(2).hex()}"
    print(f"Thay đổi field '{key}': '{old_val}' -> '{new_val}'")
    
    data = {
        'name': profile.name,
        'field_values': {key: new_val},
        'is_auto_save': 'False'
    }
    
    # 2. Gọi service
    try:
        LoanService.save_loan_form_data(profile, data, user)
        print("Đã gọi save_loan_form_data thành công.")
    except Exception as e:
        print(f"Lỗi khi gọi service: {e}")
        return

    # 3. Kiểm tra log
    log = AuditLog.objects.filter(target_model='LoanProfile', target_id=str(profile.id)).order_by('-timestamp').first()
    if log:
        print(f"Log Details: {log.details}")
        if "Cập nhật hồ sơ từ Form:" in log.details and "->" in log.details:
            print("✅ THÀNH CÔNG: Log đã được định dạng chi tiết.")
        else:
            print("❌ THẤT BẠI: Log không ở định dạng mong muốn.")
    else:
        print("❌ THẤT BẠI: Không tìm thấy log cho hồ sơ này.")

if __name__ == "__main__":
    test_loan_logging()
