
import sys
import os
import django

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ContractDraftingWebApp.settings')
django.setup()

from document_automation.views import evaluate_formula

# Mock context with redundant keys to test tripling fix
asset_202 = {'dinh_gia': '1000000000', 'id': 202, 'type': 'REALESTATE'}
asset_224 = {'dinh_gia': '1600000000', 'id': 224, 'type': 'REALESTATE'}

context = {
    'assets': [asset_202, asset_224],
    'REALESTATE': [asset_202, asset_224], # Redundant
    'realestate_list': [asset_202, asset_224], # Redundant
    'people': [{'ho_ten': 'Nguyen Van A', 'id': 1}],
    '_GENERAL_': {'so_tien_vay': 5000000000}
}

formulas = [
    # 1. Tripling Fix Verification
    ('=SUM(dinh_gia)', 2600000000.0),
    ('=SUM(ASSET.dinh_gia)', 2600000000.0),
    ('=COUNT(ASSET)', 2),
    
    # 2. Math Operations
    ('=SUBTRACT(so_tien_vay, dinh_gia)', 5000000000.0 - 2600000000.0), # 2.4B
    ('=PRODUCT(dinh_gia, 0.5)', 2600000000.0 * 0.5), # 1.3B
    ('=DIVIDE(so_tien_vay, dinh_gia)', 5000000000.0 / 2600000000.0),
    ('=ROUND(DIVIDE(so_tien_vay, dinh_gia), 2)', round(5000000000.0 / 2600000000.0, 2)),

    # 3. Logical Operations
    ('=IF(so_tien_vay > dinh_gia, "Vượt quá", "Trong tầm")', "Vượt quá"),
    ('=IF(1 < 0, "Sai", "Đúng")', "Đúng"),
    ('=IF(ho_ten, ho_ten, "Không tên")', "Nguyen Van A"),
]

print("--- Comprehensive Formula Engine Test (v2 Fix + Expansion) ---")
passed = 0
failed = 0

for f, expected in formulas:
    res = evaluate_formula(f, context)
    # Handle string vs float comparison
    match = False
    if isinstance(expected, float):
        match = abs(float(res) - expected) < 0.0001
    else:
        match = str(res) == str(expected)
        
    if match:
        print(f"✅ [PASS] Formula: {f} => Result: {res}")
        passed += 1
    else:
        print(f"❌ [FAIL] Formula: {f} => Result: {res} (Expected: {expected})")
        failed += 1

print(f"\nSummary: {passed} PASSED, {failed} FAILED.")
if failed == 0:
    print("ALL TESTS PASSED SUCCESSFULLY!")
else:
    sys.exit(1)
