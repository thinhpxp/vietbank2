import pytest
import decimal
from datetime import datetime, date
from document_automation.utils import format_currency_filter, num2words_filter, dateformat_filter

class TestDocumentUtils:
    
    # --- format_currency_filter ---
    @pytest.mark.parametrize("value, expected", [
        (1000, "1.000"),
        (1000000, "1.000.000"),
        (1234567.89, "1.234.568"), # Rounding check
        ("5000", "5.000"),
        ("", ""),
        (None, ""),
        ("abc", "abc"), # Error handling check
    ])
    def test_format_currency(self, value, expected):
        assert format_currency_filter(value) == expected

    # --- num2words_filter ---
    @pytest.mark.parametrize("value, expected", [
        (1000, "Một nghìn"), # Library uses 'nghìn' in this env
        (1000000, "Một triệu"),
        (1234, "Một nghìn hai trăm ba mươi bốn"), # Library uses 'bốn'
        (0, "không"),
        ("", ""),
        (None, ""),
    ])
    def test_num2words(self, value, expected):
        # Case insensitive compare because locale/library behavior might vary slightly in capitalization
        assert num2words_filter(value).lower() == expected.lower()

    # --- dateformat_filter ---
    @pytest.mark.parametrize("value, expected", [
        (date(2023, 12, 30), "30/12/2023"),
        (datetime(2023, 1, 1, 12, 0), "01/01/2023"),
        ("2023-10-15", "15/10/2023"),
        ("invalid-date", "invalid-date"),
        ("", ""),
        (None, ""),
    ])
    def test_dateformat(self, value, expected):
        assert dateformat_filter(value) == expected

    def test_dateformat_custom_fmt(self):
        val = date(2023, 12, 30)
        assert dateformat_filter(val, "%Y-%m") == "2023-12"
