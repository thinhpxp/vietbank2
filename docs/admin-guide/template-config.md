# Hướng dẫn cấu hình Template (.docx) dành cho Người quản trị

Tài liệu này cung cấp danh sách các trường dữ liệu (Fields) và hướng dẫn kỹ thuật để người quản trị có thể tự thiết kế và cấu hình các mẫu văn bản tự động (.docx) trong hệ thống.

---

## 1. Danh sách các Nhóm và Trường dữ liệu (Placeholders)
Sử dụng cú pháp `{{ tên_biến }}` để chèn dữ liệu vào tệp Word.

### 1.1. Nhóm: Thông tin Khách hàng (`tt-khach-hang`)
Dùng để hiển thị thông tin định danh của khách hàng trong hồ sơ. Hệ thống hỗ trợ in thông tin của một người hoặc danh sách nhiều người được phân loại theo vai trò.

**Danh sách các trường:**
1. **Họ Tên**: `{{ ho_ten }}`
2. **Số CCCD/CC/Hộ Chiếu**: `{{ cccd }}`
3. **Ngày cấp CCCD**: `{{ ngay_cap_cccd }}`
4. **Nơi cấp CCCD**: `{{ noi_cap_cccd }}`
5. **Năm sinh**: `{{ nam_sinh }}`
6. **Địa chỉ Thường trú**: `{{ dia_chi_thuong_tru }}`
7. **Số Điện Thoại**: `{{ dien_thoai }}`

**Các vai trò phổ biến (Roles):**
Một người (`person`) có thể đảm nhận một hoặc nhiều vai trò sau:
- `Bên thế chấp`: ben_the_chap
- `Bên được cấp tín dụng`: ben_duoc_cap_td
- `Người được UQ nhận tiền`: nguoi_nhan_tien

**Cách lọc danh sách theo vai trò (Ví dụ thực tiễn):**
Hệ thống cung cấp hai cách để lấy ra những người có vai trò cụ thể:

**Cách 1: Sử dụng danh sách đã lọc sẵn (Khuyên dùng)**
Hệ thống tự động tạo các danh sách con theo vai trò (tên vai trò viết thường, không dấu, nối bằng `_` và thêm hậu tố `_list`):
- `ben_the_chap_list`: Danh sách bên thế chấp tài sản.
- `ben_duoc_cap_td_list`: Danh sách bên được cấp tín dụng.
- `nguoi_nhan_tien_list`: Danh sách người nhận tiền.

*Ví dụ: Chỉ in tên những người là Bên vay:*
```
{% for p in tin_dung_list %}
- Ông/Bà: {{ p.ho_ten }}
{% endfor %}
```

**Cách 2: Lọc thủ công bằng điều kiện `if` (Dùng khi cần kiểm tra phức tạp)**
Sử dụng khi bạn đang duyệt danh sách tổng `people` và muốn lọc theo tên vai trò chính xác:
```
{% for p in people %}
  {% if "Bên vay" in p.roles %}
    - {{ p.ho_ten }} (Đây là bên vay)
  {% endif %}
{% endfor %}
```

---

### 1.2. Nhóm: Thông tin Tài sản (`tt-tai-san`)
Dùng cho các loại tài sản bảo đảm. Các trường thông tin dưới đây được gom nhóm theo loại đối tượng để bạn dễ dàng tra cứu.

**A. Thông tin chung (Áp dụng cho mọi loại tài sản):**

8. **Tên tài sản bảo đảm**: `{{ tai_san_bao_dam }}`
9. **Giá trị định giá**: `{{ dinh_gia }}`

**B. Nhóm: Bất động sản (REALESTATE):**

10. **Địa chỉ Thửa đất**: `{{ dia_chi_thua_dat }}`
11. **Thửa đất số**: `{{ thua_dat_so }}`
12. **Tờ bản đồ số**: `{{ to_ban_do }}`
13. **Diện tích**: `{{ dien_tich_thua_dat }}`
14. **Giấy CN QSDĐ số**: `{{ chung_nhan_qsdd }}`
15. **Ngày cấp GCN**: `{{ ngay_cap_gcn }}`
16. **Cơ quan cấp**: `{{ co_quan_cap }}`
17. **Số vào sổ cấp GCN**: `{{ so_vao_so }}`
18. **Loại đất / Mục đích SD**: `{{ muc_dich_sdd }}`
19. **Nguồn gốc SDĐ**: `{{ nguon_goc_sdd }}`
20. **Hình thức SD (Chung/Riêng)**: `{{ hinh_thuc_sd }}`
21. **Thời hạn SDĐ**: `{{ thoi_han_sdd }}`
22. **Thay đổi pháp lý (nếu có)**: `{{ thay_doi_phap_ly }}`

**C. Nhóm: Công trình trên đất (Thường đi kèm Bất động sản):**

23. **Địa chỉ TS GLVĐ**: `{{ dia_chi_tai_san_glvd }}`
24. **Loại nhà ở/Công trình**: `{{ loai_tai_san_glvd }}`
25. **Diện tích xây dựng**: `{{ dien_tich_xd_tsglvd }}`
26. **Tổng diện tích sử dụng**: `{{ dien_tich_sd_tsglvd }}`
27. **Kết cấu nhà**: `{{ ket_cau_tsglvd }}`
28. **Số tầng**: `{{ so_tang_tsglvd }}`

**D. Nhóm: Phương tiện / Ô tô (VEHICLE):**

29. **Nhãn hiệu xe**: `{{ nhan_hieu_xe }}`
30. **Số đăng ký xe**: `{{ dang_ky_xe }}`
31. **Số khung**: `{{ so_khung }}`
32. **Số máy**: `{{ so_may }}`

**E. Nhóm: Sổ tiết kiệm (SAVINGS):**

33. **Số thẻ STK**: `{{ stk }}`
34. **Số tiền gởi**: `{{ so_tien_goi }}`
35. **Ngày gởi**: `{{ ngay_goi_stk }}`
36. **Ngày đến hạn**: `{{ ngay_den_han_stk }}`

**F. Nhóm: Trái phiếu (BOND):**

37. **Mã trái phiếu**: `{{ ma_trai_phieu }}`
38. **Mệnh giá**: `{{ men_gia_trai_phieu }}`
39. **Kỳ hạn**: `{{ ky_han_trai_phieu }}`

**Cách sử dụng vòng lặp và Ví dụ thực tiễn:**
- **Danh sách tài sản chung**:
```
{% for asset in assets %}
- Tên TS: {{ asset.tai_san_bao_dam }}
- Giá trị định giá: {{ asset.dinh_gia | format_currency }} VNĐ
{% endfor %}
```
- **Lọc theo loại tài sản cụ thể** (Ví dụ chỉ in danh sách Bất động sản):
```
{% for x in REALESTATE %}
- Thửa đất số: {{ x.thua_dat_so }}, Tờ bản đồ số: {{ x.to_ban_do }}
- Địa chỉ: {{ x.dia_chi_thua_dat }}
{% endfor %}
```

---

### 1.3. Nhóm: Hợp đồng Tín dụng (Hạn mức & Từng lần)
Sử dụng các trường này để đổ dữ liệu liên quan đến khoản vay.

**Danh sách các trường:**
18. **Số HĐTD Từng lần**: `{{ hdtd_tl }}`
19. **Số tiền vay từng lần**: `{{ hdtd_tl_so_tien_vay }}`
20. **Hạn mức tín dụng**: `{{ hdtd_hm_so_tien_vay }}`
21. **Mục đích vay**: `{{ hdtd_tl_muc_dich_vay }}` hoặc `{{ hdtd_hm_muc_dich_vay }}`
22. **Kỳ trả lãi**: `{{ hdtd_tl_ky_tra_lai }}` hoặc `{{ hdtd_hm_ky_tra_lai }}`

**Ví dụ thực tiễn:**
Trình bày thông tin số tiền bằng số và bằng chữ trong hợp đồng:
> "Số tiền cho vay là: **{{ hdtd_tl_so_tien_vay | format_currency }}** VNĐ (Bằng chữ: *{{ hdtd_tl_so_tien_vay | num2words }}*)."

**Xử lý trường hợp có 1 hoặc cả 2 loại hợp đồng:**
Sử dụng cú pháp `if` để chỉ hiển thị phần văn bản tương ứng với dữ liệu hiện có:
```jinja2
{% if hdtd_tl %}
HỢP ĐỒNG TÍN DỤNG TỪNG LẦN:
- Số hợp đồng: {{ hdtd_tl }}
- Số tiền vay: {{ hdtd_tl_so_tien_vay | format_currency }} VNĐ
{% endif %}

{% if hdtd_hm %}
HỢP ĐỒNG TÍN DỤNG HẠN MỨC:
- Số hợp đồng: {{ hdtd_hm }}
- Hạn mức: {{ hdtd_hm_so_tien_vay | format_currency }} VNĐ
{% endif %}
```

---

### 1.4. Nhóm: Đại diện Ngân hàng (`dai_dien_bank`)
23. **Người đại diện**: `{{ nguoi_dai_dien }}`
24. **Chức vụ**: `{{ chuc_vu }}`
25. **Số ủy quyền**: `{{ uy_quyen }}`

---

## 2. Các Bộ lọc (Filters) hỗ trợ xử lý dữ liệu
Để định dạng dữ liệu, sử dụng ký hiệu `|` sau tên biến.

1. **Định dạng tiền tệ**: `{{ so_tien | format_currency }}` (VD: 1.000.000)
2. **Đọc số thành chữ**: `{{ so_tien | num2words }}` (Tiếng Việt)
3. **Định dạng ngày tháng**: `{{ ngay_cap | dateformat }}` (VD: 31/12/2024)
4. **Chuyển số sang La Mã**: `{{ so_thu_tu | to_roman }}` (VD: i, ii, iii)

---

## 3. Lưu ý quan trọng khi thiết kế
1. **Chính xác tên biến**: Phải viết đúng 100% tên trong dấu `{{ }}`.
2. **Dấu gạch dưới**: Sử dụng dấu gạch dưới `_` thay cho khoảng trắng.
3. **Dữ liệu trống**: Nếu biến không có dữ liệu, hệ thống sẽ để trống vị trí đó.

---

## 4. Template cho chế độ Tách riêng file (Batch Export)

### 4.1. Giới thiệu
Tính năng **Batch Export** cho phép xuất **n file .docx riêng biệt** từ **1 template**, mỗi file ứng với **1 đối tượng** (VD: 3 thửa đất → 3 file).

### 4.2. Cấu hình Template
1. Vào **Admin > Quản lý Mẫu Hợp đồng**
2. Khi upload hoặc sửa template, chọn **"Lặp theo"** = Loại đối tượng mong muốn (VD: Bất động sản)
3. Template này giờ sẽ tự động tick chọn "Tách riêng" khi enduser xuất văn bản

### 4.3. Cú pháp trong Template
Thay vì dùng vòng lặp `{% for asset in REALESTATE %}`, sử dụng biến đơn:

| Chế độ Gộp chung (Single) | Chế độ Tách riêng (Batch) |
|---------------------------|---------------------------|
| `{% for a in REALESTATE %}{{ a.thua_dat_so }}{% endfor %}` | `{{ thua_dat_so }}` hoặc `{{ current_asset.thua_dat_so }}` |

**Các biến hỗ trợ nâng cao**:
- `current_asset`: Chứa thông tin của đối tượng hiện tại.
- `is_batch`: Trả về `True` nếu đang ở chế độ Tách riêng file.
- `is_single`: Trả về `True` nếu đang ở chế độ Gộp chung (Single).

**Mẹo cho Template "Vạn năng" (Dùng chung cho cả 2 chế độ)**:
Nếu bạn muốn 1 template vừa có thể liệt kê tất cả tài sản (khi tải gộp), vừa có thể tách riêng từng file (khi tải tách):
```jinja2
{% set ds_tai_san = [current_asset] if is_batch else REALESTATE %}
{% for asset in ds_tai_san %}
- Tài sản: {{ asset.thua_dat_so }}
{% endfor %}
```

**Lưu ý**: 
- **Chế độ Thông minh**: Nếu bạn uncheck "Tách riêng" nhưng template có cấu hình "Lặp theo", hệ thống sẽ tự động lấy dữ liệu của **đối tượng đầu tiên** để hiển thị (thay vì để trống).
- Các field của đối tượng được flatten ra context gốc để dùng trực tiếp (VD: `{{ thua_dat_so }}`).

### 4.4. Lặp hàng trong Bảng (Tham chiếu: docxtpl v0.20.x)

> [!IMPORTANT]
> Tổng hợp từ mã nguồn `docxtpl/template.py` (hàm `patch_xml`, dòng 180-189).
> Thẻ `{%tr %}` là cú pháp mở rộng riêng của docxtpl, KHÔNG phải Jinja2 chuẩn.

#### Nguyên lý hoạt động
- `{%tr jinja2_tag %}` yêu cầu docxtpl thao tác ở **cấp độ hàng** (`<w:tr>` trong XML).
- Khi gặp thẻ `{%tr ... %}`, docxtpl sẽ **xóa toàn bộ hàng chứa thẻ đó** và thay bằng lệnh Jinja2 thuần.
- **Không có khoảng trắng** giữa `%` và `tr`: viết `{%tr` chứ KHÔNG viết `{% tr`.

#### Quy tắc bắt buộc
1. **Mỗi hàng chỉ chứa TỐI ĐA MỘT thẻ `{%tr %}`.**
2. `{%tr for %}` và `{%tr endfor %}` phải nằm ở **các hàng riêng biệt**.
3. Hàng chứa thẻ `{%tr %}` sẽ **biến mất** trong file xuất ra.

#### Cách làm trong Word (3 hàng)

Tạo bảng gồm tiêu đề + **3 hàng** bên dưới:

| STT | Địa chỉ tài sản | Giá trị (VND) |
|-----|-----------------|---------------|
| `{%tr for asset in ds_tai_san %}` | *(để trống)* | *(để trống)* |
| `{{ loop.index }}` | `Thửa số {{ asset.thua_dat_so }}, tờ bản đồ {{ asset.to_ban_do }}...` | `{{ asset.dinh_gia \| format_currency }}` |
| `{%tr endfor %}` | *(để trống)* | *(để trống)* |

**Kết quả khi xuất file:**
- **Hàng 1** (`{%tr for %}`) → Bị xóa, trở thành lệnh `{% for %}` trong XML
- **Hàng 2** (dữ liệu) → Được nhân bản N lần (N = số tài sản)
- **Hàng 3** (`{%tr endfor %}`) → Bị xóa, trở thành lệnh `{% endfor %}` trong XML

**Nhớ bổ sung dòng `{% set %}` phía trên bảng:**
```
{% set ds_tai_san = [current_asset] if is_batch else REALESTATE %}
```

**Giải thích:**
- `loop.index`: Trả về số thứ tự hiện tại (1, 2, 3...). 
- Nếu **Tách riêng**: Danh sách chỉ có 1 phần tử (`[current_asset]`) ➔ STT luôn là 1.
- Nếu **Gộp chung**: Danh sách có N tài sản (`REALESTATE`) ➔ STT tăng 1, 2, 3...

### 4.5. Ví dụ Template BM01 (Bất động sản)
```jinja2
ĐĂNG KÝ THẾ CHẤP BẤT ĐỘNG SẢN

Người thế chấp: {{ ho_ten }}
CCCD: {{ cccd }}

Thông tin thửa đất:
- Thửa số: {{ thua_dat_so }}
- Tờ bản đồ: {{ to_ban_do }}
- Diện tích: {{ dien_tich_thua_dat }}
```

### 4.6. Quy tắc đặt tên file
Tên file tự động: `TênTemplate_MãĐịnhDanh.docx`
- Mã định danh lấy từ `identity_field_key` của loại đối tượng
- VD: `BM01_012345678.docx` (CCCD), `BM02_123.docx` (ID thửa đất)

