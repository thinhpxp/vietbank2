
import sys
import os
import django

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ContractDraftingWebApp.settings')
django.setup()

from document_automation.views import evaluate_formula

asset_202 = {'dinh_gia': '1000000000', 'id': 202, 'type': 'REALESTATE'}
asset_224 = {'dinh_gia': '1600000000', 'id': 224, 'type': 'REALESTATE'}

context = {
    'assets': [asset_202, asset_224],
    'REALESTATE': [asset_202, asset_224], 
    'people': [{'ho_ten': 'Nguyen Van A', 'id': 1}],
    '_GENERAL_': {'so_tien_vay': 5000000000}
}

test_cases = [
    # [Formula, Expected, Type]
    ('=SUM(dinh_gia)', 2600000000.0, 'float'),
    ('=SUM(ASSET.dinh_gia)', 2600000000.0, 'float'),
    ('=COUNT(ASSET)', 2, 'int'),
    ('=SUBTRACT(so_tien_vay, dinh_gia)', 2400000000.0, 'float'),
    ('=PRODUCT(SUM(dinh_gia), 0.5)', 1300000000.0, 'float'),
    ('=ROUND(DIVIDE(so_tien_vay, SUM(dinh_gia)), 2)', 1.92, 'float'),
    ('=IF(so_tien_vay > SUM(dinh_gia), "Vượt quá", "Trong tầm")', "Vượt quá", 'str'),
    ('=IF(1 < 0, "Sai", "Đúng")', "Đúng", 'str'),
    ('=IF(ho_ten, ho_ten, "Không tên")', "Nguyen Van A", 'str'),
]

print("--- Final Formula Engine Test ---")
passed = 0
for f, expected, t in test_cases:
    res = evaluate_formula(f, context)
    success = False
    if t == 'float':
        success = abs(float(res) - expected) < 0.0001
    elif t == 'int':
        success = int(res) == int(expected)
    else:
        success = str(res) == str(expected)
        
    if success:
        print(f"PASS: {f} -> {res}")
        passed += 1
    else:
        print(f"FAIL: {f} -> Got '{res}' (Expected '{expected}')")

print(f"\nResult: {passed}/{len(test_cases)} PASSED")
if passed == len(test_cases):
    print("SUCCESS")
else:
    sys.exit(1)
