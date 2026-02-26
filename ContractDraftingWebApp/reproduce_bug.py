
import sys
import os
import django

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ContractDraftingWebApp.settings')
django.setup()

from document_automation.views import evaluate_formula

# Mock context as it appears in generate_document for profile 57
asset_202 = {'dinh_gia': '1000000000', 'id': 202, '_object_type': 'REALESTATE'}
asset_224 = {'dinh_gia': '1600000000', 'id': 224, '_object_type': 'REALESTATE'}

context = {
    'ten_ho_so': 'Hồ sơ 57',
    'assets': [asset_202, asset_224],
    'REALESTATE': [asset_202, asset_224],
    'realestate_list': [asset_202, asset_224],
    'people': [],
    '_GENERAL_': {}
}

formulas = [
    '=SUM(REALESTATE.dinh_gia)', # Should be 2.6B
    '=SUM(ASSET.dinh_gia)',       # Should be 2.6B (was tripled to 7.8B)
    '=SUM(dinh_gia)',             # Should be 2.6B (was tripled to 7.8B)
    '=COUNT(REALESTATE)',         # Should be 2
    '=COUNT(ASSET)',              # Should be 2 (was 6)
]

print("--- Formula Duplication Test (Diagnosis) ---")
for f in formulas:
    res = evaluate_formula(f, context)
    print(f"Formula: {f} => Result: {res:,}")
