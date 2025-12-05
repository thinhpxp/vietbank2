import locale
import decimal
from datetime import datetime, date
from num2words import num2words

# Cố gắng set locale tiếng Việt để định dạng tiền tệ (1.000.000)
# Lưu ý: Trên Windows đôi khi là 'vi_VN', trên Linux là 'vi_VN.UTF-8'
try:
    locale.setlocale(locale.LC_ALL, 'vi_VN.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'vi_VN') # Thử cho Windows
    except locale.Error:
        pass # Nếu không được thì dùng mặc định

def format_currency_filter(value):
    """Chuyển số thành dạng tiền tệ: 1000000 -> 1.000.000"""
    if not value: return ""
    try:
        d_value = decimal.Decimal(str(value)) # Chuyển về string trước để an toàn
        # Dùng locale để định dạng, hoặc dùng string format thủ công nếu locale lỗi
        return "{:,.0f}".format(d_value).replace(",", ".")
    except (ValueError, decimal.InvalidOperation):
        return str(value)

def num2words_filter(value):
    """Đọc số tiền thành chữ: 1000 -> Một nghìn"""
    if not value: return ""
    try:
        # num2words hỗ trợ tiếng Việt rất tốt
        return num2words(value, lang='vi').capitalize()
    except (ValueError, TypeError):
        return str(value)

def dateformat_filter(value, fmt="%d/%m/%Y"):
    """Định dạng ngày tháng: 2023-12-30 -> 30/12/2023"""
    if not value: return ""
    if isinstance(value, (datetime, date)):
        return value.strftime(fmt)
    try:
        # Nếu dữ liệu vào là string 'YYYY-MM-DD', parse nó ra
        date_obj = datetime.strptime(str(value), "%Y-%m-%d")
        return date_obj.strftime(fmt)
    except ValueError:
        return str(value)