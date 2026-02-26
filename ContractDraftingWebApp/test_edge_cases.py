import os
import django
import sys
import logging

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ContractDraftingWebApp.settings')
django.setup()

from document_automation.views import evaluate_formula

# Setup logging to be less noisy
logging.getLogger('document_automation').setLevel(logging.ERROR)

def test_formulas():
    context = {
        'assets': [
            {'dinh_gia': "1.000.000.000", 'dien_tich': "100,5"}, # String with dots/commas
            {'dinh_gia': 1500000000, 'dien_tich': "50,25"}
        ],
        'so_tien_vay': "2.000.000.000,00", # Full formal format
        'precision_field': "2",
        '_GENERAL_': {
            'ty_le': 0.5
        }
    }

    test_cases = [
        # 1. Decimal handling in data fields (Source of most "discrepancies")
        ('=SUM(dinh_gia)', 2500000000.0, 'Sum of mixed number/string with separators'),
        ('=SUM(dien_tich)', 150.75, 'Sum of strings with commas'),
        ('=SUB(so_tien_vay, SUM(dinh_gia))', -500000000.0, 'Sub with formal string format'),
        
        # 2. DIVIDE with multiple arguments
        ('=DIVIDE(100, 2, 5)', 10.0, 'Multi-arg DIVIDE'),
        
        # 3. ROUND with field precision or nested calls
        ('=ROUND(SUM(dien_tich), precision_field)', 150.75, 'ROUND with precision from field'),
        ('=ROUND(DIVIDE(so_tien_vay, SUM(dinh_gia)), 2)', 0.8, 'Nested calculation'),
        
        # 4. IF with numeric comparisons (Robust float check)
        ('=IF(SUM(dien_tich) > 150, "Rộng", "Hẹp")', "Rộng", 'IF comparison >'),
        ('=IF(MUL(0.5, 2) = 1, "Đúng", "Sai")', "Đúng", 'IF comparison = (dots in formula)'),
    ]

    print("--- Formula Engine Edge Case Verification ---")
    pass_count = 0
    for formula, expected, desc in test_cases:
        res = evaluate_formula(formula, context)
        
        success = False
        if isinstance(expected, float):
            try:
                success = abs(float(res) - expected) < 0.0001
            except:
                success = False
        else:
            success = str(res) == str(expected)
            
        if success:
            print(f"PASS: {formula} -> {res} ({desc})")
            pass_count += 1
        else:
            print(f"FAIL: {formula} -> Got '{res}' (Expected '{expected}') - {desc}")

    print(f"\nResult: {pass_count}/{len(test_cases)} PASSED")
    return pass_count == len(test_cases)

if __name__ == "__main__":
    test_formulas()
