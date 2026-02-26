
import sys
import os
import django

# Setup Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ContractDraftingWebApp.settings')
django.setup()

from document_automation.views import evaluate_formula

# Mock context
context = {
    'REALESTATE': [
        {'dinh_gia': '1000000', 'id': 1},
        {'dinh_gia': '2000000', 'id': 2}
    ],
    'VEHICLE': [
        {'dinh_gia': '500000', 'id': 3}
    ],
    '_GENERAL_': {
        'some_field': 'value'
    }
}

formulas = [
    '=SUM(REALESTATE.dinh_gia)',
    '=SUM(ASSET.dinh_gia)',
    '=SUM(dinh_gia)',
    '=COUNT(REALESTATE)',
    '=COUNT(ASSET)',
    '=CONCAT(REALESTATE.id, "-")'
]

print("--- Formula Backend Evaluation Test ---")
for f in formulas:
    res = evaluate_formula(f, context)
    print(f"Formula: {f} => Result: {res}")
