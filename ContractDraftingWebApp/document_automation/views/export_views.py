from django.utils import timezone
from jinja2 import Environment
from num2words import num2words
import decimal
import logging
import re
import io
import os
from datetime import datetime, date

logger = logging.getLogger(__name__)

# --- JINJA2 FILTERS ---
def format_currency_filter(value):
    if not value: return ""
    try:
        d_value = decimal.Decimal(str(value))
        return "{:,.0f}".format(d_value).replace(",", ".")
    except: return str(value)

def num2words_filter(value):
    if not value: return ""
    try:
        s_val = str(value).replace(',', '.').replace(' ', '')
        parts = s_val.split('.')
        clean_val = "".join(parts[:-1]) + "." + parts[-1] if len(parts) > 2 else s_val
        clean_val = re.sub(r'[^\d.]', '', clean_val)
        if not clean_val: return str(value)
        val_to_read = float(clean_val) if '.' in clean_val else int(clean_val)
        return num2words(val_to_read, lang='vi').capitalize()
    except Exception as e:
        logger.warning(f"num2words_filter failed: {e}")
        return str(value)

def to_roman_filter(value):
    try:
        n = int(value)
        if not 0 < n < 4000: return str(value)
        millions, hundreds, tens, ones = ["", "m", "mm", "mmm"], ["", "c", "cd", "d", "dc", "dcc", "dccc", "cm"], ["", "x", "xx", "xxx", "xl", "l", "lx", "lxx", "lxxx", "xc"], ["", "i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix"]
        return millions[n // 1000] + hundreds[(n % 1000) // 100] + tens[(n % 100) // 10] + ones[n % 10]
    except: return str(value)

def dateformat_filter(value, fmt="%d/%m/%Y"):
    empty_dots = " . . . . "
    if not value: return " . . . . . . . . " if fmt == "%d/%m/%Y" else empty_dots
    dt = None
    if isinstance(value, (datetime, date)): dt = value
    elif isinstance(value, str):
        for str_fmt in ['%Y-%m-%d', '%d/%m/%Y', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S']:
            try: dt = datetime.strptime(value.strip(), str_fmt); break
            except: continue
    if dt: return dt.strftime(fmt)
    if isinstance(value, str):
        parts = re.split(r'[/.\-]', value.strip())
        day = month = year = None
        if len(parts) == 3:
            if len(parts[0]) == 4: year, month, day = parts
            else: day, month, year = parts
        elif len(parts) == 2: month, year = parts
        def clean_part(v): return str(v).strip() if v and re.search(r'\d', str(v)) else empty_dots
        res = fmt.replace('%d', clean_part(day)).replace('%m', clean_part(month)).replace('%Y', clean_part(year))
        y_val = clean_part(year)
        res = res.replace('%y', y_val[-2:] if len(y_val) >= 2 and y_val != empty_dots else empty_dots)
        return res
    return str(value) if value else " . . . . . . . . "

# --- FORMULA ENGINE ---
def evaluate_formula(formula_str, context):
    if not formula_str or not formula_str.strip().startswith('='): return None
    return evaluate_sub_expr(formula_str.strip()[1:], context)

def evaluate_sub_expr(expr, context):
    expr = expr.strip()
    match = re.match(r'^(\w+)\((.*)\)$', expr, re.DOTALL)
    if not match: return None
    func, args_raw = match.group(1).upper(), match.group(2)
    args, current, depth, in_quote, quote_char = [], '', 0, False, ''
    for ch in args_raw:
        if ch in ('"', "'") and not in_quote: in_quote, quote_char, current = True, ch, current + ch
        elif ch == quote_char and in_quote: in_quote, current = False, current + ch
        elif not in_quote:
            if ch == '(': depth += 1
            elif ch == ')': depth -= 1
            if ch == ',' and depth == 0: args.append(current.strip()); current = ''; continue
        current += ch
    if current.strip(): args.append(current.strip())
    
    def extract_from_obj(obj, fkey):
        if not isinstance(obj, dict): return None
        for k, v in obj.items():
            if k.lower() == fkey.lower(): return v
        return None

    def to_float(val):
        if val is None or val == '': return 0.0
        if isinstance(val, (int, float)): return float(val)
        s = str(val if not isinstance(val, list) else val[0]).replace(' ', '').replace('\xa0', '').strip()
        if not s: return 0.0
        if ',' in s and '.' in s:
            if s.rfind(',') > s.rfind('.'): s = s.replace('.', '').replace(',', '.')
            else: s = s.replace(',', '')
        elif ',' in s:
            if s.count(',') > 1 or len(s.split(',')[1]) == 3: s = s.replace(',', '')
            else: s = s.replace(',', '.')
        elif '.' in s:
            if s.count('.') > 1 or len(s.split('.')[1]) == 3: s = s.replace('.', '')
        try: return float(s)
        except:
            try: return float(evaluate_sub_expr(s, context))
            except: return 0.0

    def collect_raw(arg_str):
        if not arg_str: return []
        arg_str = arg_str.strip()
        if arg_str.startswith('"') or arg_str.startswith("'"): return [arg_str.strip('"').strip("'")]
        if '(' in arg_str and ')' in arg_str:
            res = evaluate_sub_expr(arg_str, context)
            return [res] if res is not None else []
        results, tc, fk = [], None, arg_str
        if '.' in arg_str: parts = arg_str.split('.', 1); tc, fk = parts[0].upper(), parts[1]
        
        sources = []
        if tc == 'ASSET' or not tc: sources.extend(context.get('assets', []))
        if tc == 'PERSON' or (not tc and not results): sources.extend(context.get('people', []))
        if tc == '_GENERAL_' or (not tc and not results):
            gen = context.get('_GENERAL_')
            if isinstance(gen, dict): results.append(extract_from_obj(gen, fk))
        if tc and tc not in ('ASSET', 'PERSON', '_GENERAL_'):
            sources.extend(context.get(tc, []) or context.get(tc.lower(), []))
        
        for o in sources:
            v = extract_from_obj(o, fk)
            if v is not None: results.append(v)
            
        if not results and not tc:
            v_dir = context.get(arg_str) or context.get(arg_str.lower())
            if v_dir is not None and not isinstance(v_dir, (list, dict)): results.append(v_dir)
        return [r for r in results if r is not None]

    def collect_numbers(arg_list):
        nums = []
        for a in arg_list:
            raws = collect_raw(a)
            if not raws: nums.append(to_float(a))
            else: nums.extend([to_float(v) for v in raws])
        return nums

    try:
        if func == 'SUM': return sum(collect_numbers(args))
        elif func in ('PRODUCT', 'MUL'):
            vals = collect_numbers(args)
            if not vals: return 0
            res = 1.0
            for v in vals: res *= v
            return res
        elif func in ('SUBTRACT', 'SUB'):
            vals = collect_numbers(args)
            if not vals: return 0
            res = vals[0]
            for v in vals[1:]: res -= v
            return res
        elif func in ('DIVIDE', 'DIV'):
            vals = collect_numbers(args)
            if not vals: return 0
            res = vals[0]
            for v in vals[1:]:
                if v != 0: res /= v
            return res
        elif func == 'ROUND':
            v_list = collect_numbers(args[:1])
            if not v_list: return 0
            p_list = collect_numbers(args[1:]) if len(args) > 1 else [0]
            return round(v_list[0], int(p_list[0]))
        elif func == 'COUNT':
            total = 0
            for arg in args:
                if arg.startswith('"') or arg.startswith("'"): continue
                t_code = arg.strip().split('.')[0].upper() if '.' in arg else arg.strip().upper()
                if t_code == 'ASSET': total += len(context.get('assets', []))
                elif t_code == 'PERSON': total += len(context.get('people', []))
                else:
                    items = context.get(t_code, []) or context.get(t_code.lower(), [])
                    total += len(items) if isinstance(items, list) else 0
            return total
        elif func == 'AVG':
            vals = collect_numbers(args)
            return sum(vals) / len(vals) if vals else 0
        elif func == 'MIN': vals = collect_numbers(args); return min(vals) if vals else 0
        elif func == 'MAX': vals = collect_numbers(args); return max(vals) if vals else 0
        elif func == 'CONCAT':
            sep_arg = next((a for a in args if a.startswith('"') or a.startswith("'")), None)
            separator = sep_arg.strip().strip('"').strip("'") if sep_arg else ', '
            final_texts = [str(r) for a in args if a != sep_arg for r in collect_raw(a)]
            return separator.join(final_texts)
        elif func == 'IF':
            if len(args) < 3: return ""
            cond_raw, is_true = args[0], False
            for op in ('>=', '<=', '>', '<', '='):
                if op in cond_raw:
                    l_s, r_s = cond_raw.split(op, 1)
                    l_v, r_v = (collect_numbers([l_s.strip()])[0] if collect_raw(l_s.strip()) else to_float(l_s.strip())), (collect_numbers([r_s.strip()])[0] if collect_raw(r_s.strip()) else to_float(r_s.strip()))
                    if op == '>=': is_true = l_v >= r_v
                    elif op == '<=': is_true = l_v <= r_v
                    elif op == '>': is_true = l_v > r_v
                    elif op == '<': is_true = l_v < r_v
                    elif op == '=':
                        try: is_true = abs(float(l_v) - float(r_v)) < 0.000001
                        except: is_true = str(l_v) == str(r_v)
                    break
            else:
                raw_cond = collect_raw(cond_raw)
                is_true = bool(raw_cond[0]) if raw_cond else bool(cond_raw.strip().replace('"', '').replace("'", ""))
            res_key = args[1] if is_true else args[2]
            lookup = collect_raw(res_key)
            return lookup[0] if lookup else res_key.strip('"').strip("'")
        return None
    except Exception as e:
        logger.error(f"evaluate_sub_expr error for '{expr}': {e}")
        return None

# --- FILENAME CLEANER ---
def clean_filename(name):
    if not name: return "document"
    s = str(name)
    chars = {'àáạảãâầấậẩẫăằắặẳẵ': 'a', 'ÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴ': 'A', 'èéẹẻẽêềếệểễ': 'e', 'ÈÉẸẺẼÊỀẾỆỂỄ': 'E', 'òóọỏõôồốộổỗơờớợởỡ': 'o', 'ÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠ': 'O', 'ìíịỉĩ': 'i', 'ÌÍỊỈĨ': 'I', 'ùúụủũưừứựửữ': 'u', 'ÙÚỤỦŨƯỪỨỰỬỮ': 'U', 'ỳýỵỷỹ': 'y', 'ỲÝỴỶỸ': 'Y', 'đ': 'd', 'Đ': 'D'}
    for k, v in chars.items(): s = re.sub(f'[{k}]', v, s)
    s = re.sub(r'[\\/*?:"<>|]', '_', s).replace(" ", "_")
    return re.sub(r'[^\x00-\x7f]', r'', s)
