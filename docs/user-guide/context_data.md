# Cấu trúc Dữ liệu cho Template Word (.docx)

Tài liệu này mô tả chi tiết các biến (context) có sẵn khi bạn xây dựng mẫu hợp đồng.

## 1. Biến hệ thống & Thông tin chung
Các biến này có thể sử dụng trực tiếp ở bất kỳ đâu trong văn bản bằng cú pháp `{{ ten_bien }}`.

| Biến | Mô tả | Định dạng / Ví dụ |
| :--- | :--- | :--- |
| `ten_ho_so` | Tên hồ sơ vay | "Hồ sơ vay Nguyễn Văn A" |
| `ngay_tao` | Ngày lập hồ sơ (Lấy từ ngày tạo hồ sơ trên hệ thống) | "21/01/2026" |

## 2. Các Trường Động (General Fields)
Đây là các trường thuộc nhóm **"Thông tin Khoản vay"**. Chúng xuất hiện trực tiếp trong form chính.

| Placeholder Key | Nhãn (Label) | Ghi chú |
| :--- | :--- | :--- |
| `hdtc` | HĐTC | Số hợp đồng thế chấp |
| `hdtd` | HĐTD | Số hợp đồng tín dụng |
| `ngay_hop_dong` | Ngày xác lập | Ngày ký kết các hợp đồng |
| `so_tien_vay` | Số tiền vay | Số tiền vay/hạn mức vay |
| `tong_gia_tri_tai_san` | Tổng giá trị tài sản | Tổng giá trị của các TSBĐ |

*Sử dụng:* `{{ so_tien_vay | format_currency }}`

## 3. Danh sách Người liên quan (People)
Dữ liệu người dùng được gửi dưới dạng danh sách (List).

### Biến danh sách chính:
- `people`: Tất cả người trong hồ sơ.

#### 1. Danh sách theo Vai trò (Động):
Hệ thống tự động tạo các danh sách dựa trên **Mã định danh (Slug)** của Vai trò.
- Cú pháp: `{{ slug }}_list`
- Ví dụ: `ben_vay_list`, `ben_the_chap_list`, `nguoi_thua_ke_list`.

### Các thuộc tính bên trong mỗi người (person):
Khi dùng trong vòng lặp `{%tr for p in people %}`, bạn truy cập bằng `p.key_name`.

| Key | Nhãn | Ghi chú |
| :--- | :--- | :--- |
| `ho_ten` | Họ Tên | |
| `cccd` | CCCD/CC/Hộ Chiếu | Số căn cước công dân |
| `noi_cap_cccd` | Nơi cấp CCCD | |
| `ngay_cap_cccd` | Ngày cấp CC | |
| `nam_sinh` | Năm sinh | Ngày tháng năm sinh |
| `dia_chi_thuong_tru` | Địa chỉ Thường trú | |
| `dien_thoai` | Số Điện Thoại | |
| `roles` | Danh sách vai trò | Dạng mảng (ví dụ: ["Bên vay"]) |

*Ví dụ vòng lặp:*
```jinja2
{% for p in ben_vay_list %}
Ông/Bà: {{ p.ho_ten }}
Số CCCD: {{ p.cccd }}
{% endfor %}
```

## 4. Danh sách Tài sản (Assets)
Dữ liệu tài sản được gửi dưới dạng danh sách (List).

### Biến danh sách chính:
- `assets`: Tất cả tài sản trong hồ sơ (không phân biệt loại).

#### 1. Danh sách theo Loại đối tượng (Động):
Hệ thống tự động phân loại tài sản vào các biến dựa trên **Mã loại đối tượng (Object Type)**.
- Cú pháp 1 (Viết hoa): `REALESTATE`, `VEHICLE`, `SAVINGBOOK`, `BOND`...
- Cú pháp 2 (Lowercase + list): `realestate_list`, `vehicle_list`, ...

### Các thuộc tính bên trong mỗi tài sản (asset):
Hệ thống hỗ trợ nhiều loại tài sản khác nhau. Dưới đây là các key phổ biến:

| Key | Nhãn | Loại TS |
| :--- | :--- | :--- |
| `chung_nhan_qsdd` | Giấy CN QSDĐ | Bất động sản |
| `thua_dat_so` | Thửa đất số | Bất động sản |
| `to_ban_do` | Tờ bản đồ | Bất động sản |
| `dien_tich_thua_dat` | Diện tích | Bất động sản |
| `dia_chi_thua_dat` | Địa chỉ Thửa đất | Bất động sản |
| `dang_ky_xe` | Số đăng ký | Xe cộ |
| `nhan_hieu_xe` | Nhãn hiệu | Xe cộ |
| `so_khung` | Số khung | Xe cộ |
| `so_may` | Số máy | Xe cộ |
| `stk` | Số STK | Sổ tiết kiệm |
| `so_tien_goi` | Số tiền gởi | Sổ tiết kiệm |
| `ma_trai_phieu` | Mã trái phiếu | Trái phiếu |
| `tai_san_bao_dam` | Tài sản bảo đảm | Mô tả tổng hợp |
| `dinh_gia` | Định giá | Giá trị tài sản |

*Ví dụ lặp theo loại cụ thể (Bất động sản):*
```jinja2
{%tr for as in REALESTATE %}
- Tài sản: {{ as.tai_san_bao_dam }}
- Trị giá: {{ as.dinh_gia | format_currency }} VNĐ
{%tr endfor %}
```

*Ví dụ lặp tất cả tài sản trong hồ sơ:*
```jinja2
{%tr for item in assets %}
- {{ loop.index }}. {{ item.tai_san_bao_dam }}
{%tr endfor %}
```

---

## 5. Các Bộ lọc (Filters) hỗ trợ
Sử dụng sau dấu gạch đứng `|`.

1. **Tiền tệ:** `{{ gia_tri | format_currency }}` 
   - Đầu vào: `1000000` -> Kết quả: `1.000.000`
2. **Số thành chữ:** `{{ gia_tri | num2words }}` 
   - Đầu vào: `1200000` -> Kết quả: `Một triệu hai trăm nghìn`
3. **Ngày tháng thông minh:** `{{ ngay | dateformat('%d/%m/%Y') }}`
   - Cơ chế: Nếu trường ngày bị trống, hệ thống tự điền dấu chấm `.. / .. / ....`
4. **Nối mảng:** `{{ p.roles | join(', ') }}`
5. **Số La Mã:** `({{ loop.index | to_roman }})` -> `(i)`, `(ii)`, `(iii)`...

---

## 6. Lưu ý quan trọng khi soạn thảo mẫu Word
Để tránh lỗi "Server Error" (unknown tag) do cấu trúc XML của Word gây ra, bạn nên tuân thủ các quy tắc sau:

1. **Ưu tiên tách dòng các thẻ điều khiển:**
   - **Nên:** 
     ```jinja2
     {%p for as in REALESTATE %}
     {% if assets | length > 1 %}
     ...
     {% endif %}
     {%p endfor %}
     ```
   - **Không nên:** Viết dính chùm các thẻ trên cùng một dòng (ví dụ: `{%p for ... %}{% if ... %}`).
   
2. **Xóa định dạng (Clear Formatting):** Nếu thẻ bị báo lỗi dù đã viết đúng, hãy bôi đen thẻ đó và nhấn **Clear All Formatting** trong Word. Điều này giúp loại bỏ các mã XML ẩn (như kiểm tra chính tả) xen vào giữa các ký tự của thẻ.

3. **Phân biệt Thẻ Inline (Trên cùng 1 dòng) và Thẻ Cấu trúc (Paragraph/Table):**
   - **Thẻ Inline (Dùng trên cùng 1 dòng):** Chỉ sử dụng cú pháp tiêu chuẩn `{% ... %}` (không có chữ `p`, `tr`, `tc`).
     - *Ví dụ:* `Tài sản: {{ as.tai_san }} {% if as.dinh_gia %}(Giá: {{ as.dinh_gia }}){% endif %}`. Cách này an toàn để viết chung dòng với văn bản khác.
   - **Thẻ Cấu trúc (Dùng để lặp đoạn văn hoặc bảng):** Phải sử dụng `{%p ... %}` cho đoạn văn, `{%tr ... %}` cho dòng trong bảng. 
     - *Quy tắc:* Khi đã dùng `p`, `tr`, `tc`, bạn **bắt buộc** phải để chúng ở các dòng riêng biệt hoặc các ô riêng biệt để tránh làm loạn cấu trúc XML của Word.

4. **Sử dụng thẻ `{%p ... %}` đúng cách:** Thẻ có chữ `p` (`{%p for %}`, `{%p if %}`) sẽ tác động lên toàn bộ đoạn văn (paragraph). Nếu bạn dùng thẻ này, hãy để nó ở một dòng riêng.

---
*Tài liệu được cập nhật tự động từ cấu hình hệ thống ngày 21/01/2026.*
