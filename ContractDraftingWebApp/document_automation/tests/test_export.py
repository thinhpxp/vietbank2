import pytest
import decimal
from datetime import datetime, date
from document_automation.views.export_views import (
    format_currency_filter, num2words_filter, dateformat_filter,
    to_roman_filter, evaluate_formula, clean_filename
)

class TestExportLogic:
    
    # --- Filters ---
    def test_format_currency(self):
        assert format_currency_filter(1000000) == "1.000.000"
        assert format_currency_filter(None) == ""

    def test_num2words(self):
        # The implementation in export_views.py is slightly different (uses float/int cast)
        assert "một triệu" in num2words_filter(1000000).lower()

    def test_to_roman(self):
        assert to_roman_filter(1) == "i"
        assert to_roman_filter(10) == "x"
        assert to_roman_filter(2024) == "mmxxiv"

    def test_dateformat(self):
        dt = date(2023, 12, 30)
        assert dateformat_filter(dt) == "30/12/2023"
        assert dateformat_filter(None) == " . . . . . . . . "

    # --- Formula Engine (Python version) ---
    @pytest.fixture
    def mock_context(self):
        return {
            '_GENERAL_': {'interest_rate': 8.5},
            'people': [
                {'ho_ten': 'Nguyen Van A', 'age': 30},
                {'ho_ten': 'Tran Thi B', 'age': 25}
            ],
            'assets': [
                {'gia_tri': 1000000},
                {'gia_tri': 2000000}
            ]
        }

    def test_evaluate_formula_basic(self, mock_context):
        assert evaluate_formula("=SUM(10, 20)", mock_context) == 30.0
        assert evaluate_formula("=MUL(2, 5)", mock_context) == 10.0

    def test_evaluate_formula_context(self, mock_context):
        # Test SUM over assets
        assert evaluate_formula("=SUM(ASSET.gia_tri)", mock_context) == 3000000.0
        # Test COUNT
        assert evaluate_formula("=COUNT(PERSON)", mock_context) == 2

    def test_evaluate_formula_if(self, mock_context):
        assert evaluate_formula("=IF(SUM(ASSET.gia_tri) > 1000, 'Expensive', 'Cheap')", mock_context) == 'Expensive'

    # --- Filename cleaner ---
    def test_clean_filename(self):
        assert clean_filename("Hợp đồng vay vốn") == "Hop_dong_vay_von"
        assert clean_filename("File!*#") == "File!_#"
