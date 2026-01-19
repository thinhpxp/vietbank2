# Cấu trúc Dữ liệu cho Template Word (.docx)

Tài liệu này mô tả chi tiết các biến (context) có sẵn khi bạn xây dựng mẫu hợp đồng.

## 1. Biến hệ thống & Thông tin chung
Các biến này có thể sử dụng trực tiếp ở bất kỳ đâu trong văn bản bằng cú pháp `{{ ten_bien }}`.

| Biến | Mô tả | Định dạng / Ví dụ |
| :--- | :--- | :--- |
| `ten_ho_so` | Tên hồ sơ vay | "Hồ sơ vay Nguyễn Văn A" |
| `ngay_tao` | Ngày lập hồ sơ (Ưu tiên lấy từ trường "Ngày lập hồ sơ" nếu có điền, nếu không sẽ lấy ngày tạo hồ sơ trên hệ thống) | "25/12/2025" hoặc rỗng |

> [!TIP]
> **Cách điều chỉnh ngày tháng:**
> Bạn có thể tìm trường **"Ngày lập hồ sơ"** trong phần **Thông tin Hồ sơ** để tự nhập ngày (quá khứ/tương lai). 
> - Nếu bạn muốn ngày tháng bị **để trống** trong hợp đồng để ghi tay sau, hãy để trống trường này trong giao diện.


## 2. Các Trường Động (General Fields)
Đây là các trường thuộc nhóm "Thông tin Hồ sơ" hoặc "Thông tin khoản vay" (thường không gắn với từng người cụ thể).

| Placeholder Key | Nhãn (Label) | Nhóm |
| :--- | :--- | :--- |
| `hop_dong_the_chap` | Hợp đồng thế chấp số | Thông tin Hồ sơ |
| `hop_dong_tin_dung` | Hợp đồng tín dụng số | Thông tin Hồ sơ |
| `so_tien_vay` | Số tiền vay | Thông tin khoản vay |
| `thoi_han_vay` | Thời hạn vay | Thông tin khoản vay |
| `lai_suat_vay` | Lãi suất | Thông tin khoản vay |
| `muc_dich_vay` | Mục đích vay | Thông tin khoản vay |
| `tong_gia_tri_tai_san` | Tổng giá trị TSBĐ | Thông tin khoản vay |

*Sử dụng:* `{{ so_tien_vay | format_currency }}`

## 3. Danh sách Người liên quan (People)
Dữ liệu người dùng được gửi dưới dạng danh sách (List).

### Biến danh sách chính:
- `people`: Tất cả người trong hồ sơ.

#### 1. Danh sách theo Vai trò (Động):
Hệ thống tự động tạo các danh sách dựa trên **Mã định danh (Slug)** của Vai trò được cấu hình trong Admin.
- Cú pháp: `{{ slug }}_list`
- Ví dụ: Nếu vai trò "Người thừa kế" có slug là `nguoi_thua_ke` -> Sử dụng: `nguoi_thua_ke_list`.

#### 2. Danh sách mặc định (Tương thích ngược):
- `ben_duoc_cap_tin_dung_list`: Những người có vai trò "Bên được cấp tín dụng".
- `ben_the_chap_list`: Những người có vai trò "Bên thế chấp".
- `ben_vay_list`: Tương đương `ben_duoc_cap_tin_dung_list`.
- `ben_bao_dam_list`: Tương đương `ben_the_chap_list`.
- `ben_bao_lanh_list`: Những người có vai trò "Bên bảo lãnh".

### Các thuộc tính bên trong mỗi người (person):
Khi dùng trong vòng lặp `{%tr for p in people %}`, bạn truy cập bằng `p.key_name`.

| Key | Nhãn |
| :--- | :--- |
| `ho_ten` | Họ tên |
| `cccd_so` | Số CCCD |
| `cccd` | Số CCCD (trường động) |
| `noi_cap_cccd` | Nơi cấp CCCD |
| `ngay_cap_cccd` | Ngày cấp CCCD |
| `dia_chi_thuong_tru` | Địa chỉ thường trú |
| `cif` | Mã CIF |
| `roles` | Danh sách vai trò (mảng) |

*Ví dụ vòng lặp:*
```jinja2
{% for p in ben_duoc_cap_tin_dung_list %}
Ông/Bà: {{ p.ho_ten }}
Số CCCD: {{ p.cccd_so }}
{% endfor %}
```

## 4. Danh sách Tài sản (Assets)
Tương tự như người liên quan, dữ liệu tài sản được gửi dưới dạng danh sách `assets`.

### Biến danh sách chính:
- `assets`: Tất cả tài sản trong hồ sơ.

### Các thuộc tính bên trong mỗi tài sản (asset):
Khi dùng trong vòng lặp `{%tr for as in assets %}`, bạn truy cập bằng `as.key_name`.

| Key | Nhãn |
| :--- | :--- |
| `so_giay_chung_nhan` | Giấy chứng nhận số |
| `so_vao_so` | Số vào sổ |
| `ngay_cap_tai_san` | Ngày cấp |
| `to_ban_do` | Tờ bản đồ số |
| `thua_dat_so` | Thửa đất số |
| `dien_tich_thua_dat` | Diện tích |
| `dia_chi_tai_san` | Địa chỉ tài sản |
| `gia_tri_tsbd` | Giá trị TSBĐ |

*Ví dụ vòng lặp trong bảng:*
```
DANH MỤC TÀI SẢN:
{%tr for as in assets %}
- Thửa đất số: {{ as.thua_dat_so }}, Diện tích: {{ as.dien_tich_thua_dat }} m2
- Địa chỉ: {{ as.dia_chi_tai_san }}
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
   - Cơ chế: Nếu trường ngày bị trống, hệ thống tự điền dấu chấm `.. / .. / ....` để ký tay.
4. **Nối mảng:** `{{ p.roles | join(', ') }}`
5. **Số La Mã:** `({{ loop.index | to_roman }})`
   - Kết quả: `(i)`, `(ii)`, `(iii)`...

---
*Tài liệu được xuất tự động từ hệ thống ngày 24/12/2025.*
