# Cấu trúc Dữ liệu cho Template Word (.docx)

Tài liệu này mô tả chi tiết các biến (context) có sẵn khi bạn xây dựng mẫu hợp đồng. 

---

## 1. Biến hệ thống & Thông tin chung
Các biến này có thể sử dụng trực tiếp ở bất kỳ đâu trong văn bản bằng cú pháp `{{ ten_bien }}`.

| Biến | Mô tả | Định dạng / Ví dụ |
| :--- | :--- | :--- |
| `ten_ho_so` | Tên hồ sơ vay | "Hồ sơ vay Nguyễn Văn A" |
| `ngay_tao` | Ngày lập hồ sơ (Lấy từ ngày tạo hồ sơ) | "21/01/2026" |
| `today` | Ngày hiện tại (Lúc xuất file) | "27/01/2026" |

---

## 2. Các Trường Thông tin Hồ sơ (Profile Fields)
Đây là các trường thuộc nhóm **"Thông tin Khoản vay"** và **"Thông tin Khách hàng"**. Chúng xuất hiện trực tiếp trong form chính.

| Placeholder Key | Nhãn (Label) | Ghi chú |
| :--- | :--- | :--- |
| `hdtc` | HĐTC | Số hợp đồng thế chấp |
| `hdtd` | HĐTD | Số hợp đồng tín dụng |
| `ngay_hop_dong` | Ngày xác lập | Ngày ký kết các hợp đồng |
| `so_tien_vay` | Số tiền vay | Số tiền vay/hạn mức vay |
| `tong_gia_tri_tai_san` | Tổng giá trị tài sản | Tổng giá trị của các TSBĐ |
| `ho_ten` | Họ Tên | Tên khách hàng chính |
| `cccd` | CCCD/CC/Hộ Chiếu | Số căn cước công dân |
| `dia_chi_thuong_tru` | Địa chỉ Thường trú | |

*Sử dụng:* `{{ so_tien_vay | format_currency }}`

---

## 3. Danh sách Người liên quan (People)
Dữ liệu người dùng được gửi dưới dạng danh sách (List).

### Biến danh sách chính:
- `people`: Tất cả người trong hồ sơ.

#### Danh sách theo Vai trò (Động):
Hệ thống tự động tạo các danh sách dựa trên **Mã định danh (Slug)** của Vai trò.
- Cú pháp: `{{ slug }}_list`
- Ví dụ: `ben_the_chap_list`, `ben_duoc_cap_td_list`.

### Các thuộc tính bên trong mỗi người (person):
| Key | Nhãn | Ghi chú |
| :--- | :--- | :--- |
| `ho_ten` | Họ Tên | |
| `cccd` | CCCD/CC/Hộ Chiếu | |
| `noi_cap_cccd` | Nơi cấp | |
| `ngay_cap_cccd` | Ngày cấp | |
| `nam_sinh` | Năm sinh | |
| `dia_chi_thuong_tru` | Địa chỉ | |
| `dien_thoai` | Số Điện Thoại | |

*Ví dụ:*
```jinja2
{% for p in ben_the_chap_list %}
Ông/Bà: {{ p.ho_ten }} - Số CCCD: {{ p.cccd }}
{% endfor %}
```

---

## 4. Danh sách Tài sản (Assets)
Dữ liệu tài sản được gửi dưới dạng danh sách (List).

### Biến danh sách chính:
- `assets`: Tất cả tài sản trong hồ sơ (không phân biệt loại).

#### Danh sách theo Loại đối tượng:
Hệ thống tự động phân loại tài sản vào các biến dựa trên **Object Type**.
- Cú pháp 1 (Viết hoa): `REALESTATE`, `VEHICLE`, `SAVINGS`, `BOND`, `INSURANCE`, `CONTRACT`.
- Cú pháp 2 (Lowercase + list): `realestate_list`, `vehicle_list`, `savings_list`...

### Các thuộc tính phổ biến cho Tài sản:
| Key | Nhãn | Loại áp dụng |
| :--- | :--- | :--- |
| `tai_san_bao_dam` | Mô tả tổng hợp | Tất cả |
| `dinh_gia` | Định giá | Tất cả |
| `chung_nhan_qsdd` | Giấy CN QSDĐ | Bất động sản |
| `thua_dat_so` | Thửa đất số | Bất động sản |
| `to_ban_do` | Tờ bản đồ | Bất động sản |
| `dien_tich_thua_dat` | Diện tích | Bất động sản |
| `dia_chi_thua_dat` | Địa chỉ | Bất động sản |
| `dang_ky_xe` | Số đăng ký | Xe cộ |
| `so_khung` / `so_may` | Số khung / máy | Xe cộ |
| `stk` | Số STK | Sổ tiết kiệm |
| `so_tien_goi` | Số tiền gởi | Sổ tiết kiệm |
| `ma_trai_phieu` | Mã trái phiếu | Trái phiếu |

*Ví dụ:*
```jinja2
{%tr for as in REALESTATE %}
- {{ as.tai_san_bao_dam }} (Trị giá: {{ as.dinh_gia | format_currency }})
{%tr endfor %}
```

---

## 5. Khu vực đặc thù (Dedicated Sections)
Dành cho các đối tượng hiển thị riêng. Bạn có thể truy cập **trực tiếp** các trường này mà không cần vòng lặp.

### Đại diện Ngân Hàng (ATTORNEY)
| Key | Nhãn |
| :--- | :--- |
| `nguoi_dai_dien` | Người đại diện |
| `cccd_bank` | Số CCCD |
| `chuc_vu` | Chức vụ |
| `uy_quyen` | Số ủy quyền |

*Sử dụng:* `Ông/Bà: {{ nguoi_dai_dien }} theo văn bản số {{ uy_quyen }}.`

---

## 6. Các Bộ lọc (Filters) hỗ trợ
1. **Tiền tệ:** `{{ x | format_currency }}` (1000000 -> 1.000.000)
2. **Số thành chữ:** `{{ x | num2words }}` (1.2M -> Một triệu hai trăm nghìn)
3. **Ngày tháng:** `{{ x | dateformat('%d/%m/%Y') }}` (Trống -> .. / .. / ....)
4. **Số La Mã:** `{{ loop.index | to_roman }}` (1 -> i, 2 -> ii)

---
*Cập nhật cấu hình mới nhất ngày 27/01/2026.*
