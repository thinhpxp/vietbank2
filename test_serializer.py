import os
import django
import sys

# Setup Django
sys.path.append(r'c:\Users\thinhpxp\Webapp_vietbank\ContractDraftingWebApp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ContractDraftingWebapp.settings')
django.setup()

from document_automation.models import MasterObject, LoanProfile
from document_automation.serializers import MasterObjectSerializer
from rest_framework.test import APIRequestFactory

def test():
    # Giả định ID của hồ sơ và đối tượng (Dựa trên thông tin người dùng cung cấp)
    profile_id = 72
    contract_id = 2100 # ID của CONTRACT_HDTC? Hoặc dùng search để tìm
    
    profile = LoanProfile.objects.get(id=profile_id)
    # Tìm đối tượng CONTRACT_HDTC có trong hồ sơ
    link = profile.object_links.filter(master_object__object_type='CONTRACT_HDTC').first()
    if not link:
        print("Error: No CONTRACT_HDTC found in profile 72")
        return
    
    contract = link.master_object
    print(f"Testing Contract ID: {contract.id}")
    
    # Giả lập Request với query param loan_profile_id
    factory = APIRequestFactory()
    request = factory.get(f'/api/master-objects/{contract.id}/', {'loan_profile_id': str(profile_id)})
    
    # Khởi tạo Serializer với context
    serializer = MasterObjectSerializer(contract, context={'request': request})
    
    data = serializer.data
    print(f"Additional Info (with profile context): {data.get('additional_info')}")
    
    # Kiểm tra không có context
    serializer_no_ctx = MasterObjectSerializer(contract)
    data_no_ctx = serializer_no_ctx.data
    print(f"Additional Info (Universal): {data_no_ctx.get('additional_info')}")

if __name__ == "__main__":
    test()
