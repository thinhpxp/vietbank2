# Hướng dẫn Tạo Template Word (.docx)

Tài liệu này hướng dẫn cách tạo các file mẫu Word để sinh hợp đồng tự động trong ứng dụng.

## Thư viện sử dụng

Ứng dụng sử dụng **docxtpl** (python-docx-template) - một thư viện kết hợp `python-docx` và `Jinja2` để sinh file Word từ template.

**Tài liệu tham khảo:**
- [docxtpl Documentation](https://docxtpl.readthedocs.io/en/latest/)
- [Jinja2 Template Documentation](https://jinja.palletsprojects.com/en/3.1.x/templates/)

---

## Cú pháp cơ bản

### 1. Chèn biến đơn giản

Sử dụng cú pháp `{{ }}` để chèn giá trị:

```
Tên hồ sơ: {{ ten_ho_so }}
Ngày tạo: {{ ngay_tao }}
Số tiền vay: {{ so_tien_vay }}
```

### 2. Sử dụng Filter (Bộ lọc)

Ứng dụng đã đăng ký các filter sau:

| Filter | Mô tả | Ví dụ |
|--------|-------|-------|
| `format_currency` | Định dạng số thành tiền VND | `{{ so_tien | format_currency }}` → `1.000.000` |
| `num2words` | Chuyển số thành chữ Tiếng Việt | `{{ so_tien | num2words }}` → `Một triệu` |
| `dateformat` | Định dạng ngày tháng | `{{ ngay_cap | dateformat('%d/%m/%Y') }}` |
| `to_roman` | Chuyển số sang chữ La Mã | `({{ loop.index | to_roman }})` → `(i)` |

**Ví dụ kết hợp:**
```
Số tiền: {{ so_tien_vay | format_currency }} đồng (Bằng chữ: {{ so_tien_vay | num2words }} đồng)
```

---

## Làm việc với danh sách (People, Assets)

### 3. Vòng lặp cơ bản (Trong đoạn văn/Danh sách)

Sử dụng cú pháp Jinja2 chuẩn để lặp qua danh sách trong đoạn văn thông thường hoặc danh sách có dấu đầu dòng (Bullet points):

```
{% for p in ben_bao_dam_list %}
- **Ông/Bà: {{ p.ho_ten }}**
  - Số CCCD: {{ p.cccd_so }}
{% endfor %}
```

> [!IMPORTANT]
> **Sự khác biệt cực kỳ quan trọng:**
> - **`{% ... %}`**: Dùng cho văn bản bình thường, danh sách liệt kê.
> - **`{%tr ... %}`**: CHỈ DÙNG TRONG BẢNG (Table). Nó sẽ nhân bản toàn bộ **dòng (row)** của bảng. Nếu bạn dùng `{%tr %}` ở ngoài bảng, hệ thống sẽ báo lỗi **500 (Internal Server Error)**.

### 4. Vòng lặp trong bảng

```
{%tr for person in people %}
| {{ person.ho_ten }} | {{ person.cccd_so }} | {{ person.dia_chi }} |
{%tr endfor %}
```

### 5. Danh sách lọc sẵn

Ứng dụng cung cấp các danh sách lọc theo vai trò:

| Biến | Mô tả |
|------|-------|
| `people` | Tất cả người liên quan |
| `ben_vay_list` | Những người có vai trò "Bên Vay" |
| `ben_bao_dam_list` | Những người có vai trò "Bên Bảo đảm" |

**Ví dụ:**
```
BÊN VAY:
{%tr for p in ben_vay_list %}
- Ông/Bà {{ p.ho_ten }}, CCCD số {{ p.cccd_so }}
{%tr endfor %}
```

---

## Các biến có sẵn (Context)

### Thông tin hồ sơ
| Biến | Mô tả |
|------|-------|
| `ten_ho_so` | Tên hồ sơ vay |
| `ngay_tao` | Ngày tạo hồ sơ (đã format dd/mm/yyyy) |

### Các trường động
Tất cả các trường được tạo trong Admin → Quản lý Trường sẽ có biến tương ứng với `placeholder_key`.

**Ví dụ:** Nếu tạo trường với `placeholder_key = "so_hop_dong"` → Dùng `{{ so_hop_dong }}`

### Thông tin người (trong vòng lặp)
| Biến | Mô tả |
|------|-------|
| `person.ho_ten` | Họ tên |
| `person.cccd_so` | Số CCCD |
| `person.roles` | Danh sách vai trò |
| `person.[placeholder_key]` | Các trường động khác |

---

## Điều kiện (Conditions)

### 6. Hiển thị có điều kiện

```
{% if so_tien_vay %}
Số tiền vay: {{ so_tien_vay | format_currency }} VND
{% endif %}
```

### 7. Kiểm tra vai trò

```
{% if 'Bên Vay' in person.roles %}
(Bên vay)
{% endif %}
```

---

## Lưu ý quan trọng

1. **Tên biến:** Phải khớp chính xác với `placeholder_key` trong hệ thống
2. **Khoảng trắng:** Không để khoảng trắng thừa trong `{{ }}`
3. **Encoding:** Lưu file với encoding UTF-8
4. **Test:** Luôn test template với dữ liệu mẫu trước khi dùng thực tế

---

## Mẹo trình bày: Ngày tháng viết tay

Nếu bạn muốn tạo khoảng trống đẹp mắt khi dữ liệu ngày tháng bị để trống (để ký tay sau), hãy sử dụng cấu trúc `if/else`:

**Cú pháp đề xuất:**
```jinja2
ngày {% if ngay_tao %}{{ ngay_tao | dateformat('%d') }}{% else %}............{% endif %} tháng {% if ngay_tao %}{{ ngay_tao | dateformat('%m') }}{% else %}............{% endif %} năm {% if ngay_tao %}{{ ngay_tao | dateformat('%Y') }}{% else %}................{% endif %}
```

- **Khi có dữ liệu:** ngày 25 tháng 12 năm 2025
- **Khi để trống:** ngày ............ tháng ............ năm ................

---

## Ví dụ Template hoàn chỉnh

```
HỢP ĐỒNG THẾ CHẤP
Số: {{ so_hop_dong }}

Hôm nay, ngày {{ ngay_ky | dateformat('%d') }} tháng {{ ngay_ky | dateformat('%m') }} năm {{ ngay_ky | dateformat('%Y') }}

BÊN CHO VAY: NGÂN HÀNG TMCP VIỆT NAM THƯƠNG TÍN

BÊN VAY:
{%tr for p in ben_vay_list %}
- Ông/Bà: {{ p.ho_ten }}
  CCCD số: {{ p.cccd_so }}, cấp ngày {{ p.ngay_cap_cccd | dateformat }}
  Địa chỉ: {{ p.dia_chi }}
{%tr endfor %}

1. SỐ TIỀN VAY: {{ so_tien_vay | format_currency }} VND
   (Bằng chữ: {{ so_tien_vay | num2words }} đồng Việt Nam)

2. MỤC ĐÍCH VAY: {{ muc_dich_vay }}

3. THỜI HẠN VAY: {{ thoi_han_vay }} tháng

...
```

---

## Tài liệu tham khảo thêm

- **docxtpl GitHub:** https://github.com/elapouya/python-docx-template
- **Jinja2 Filters:** https://jinja.palletsprojects.com/en/3.1.x/templates/#filters
- **python-docx:** https://python-docx.readthedocs.io/en/latest/
