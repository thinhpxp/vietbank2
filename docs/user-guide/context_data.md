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
Đây là các trường thông tin chung không gắn với bất kỳ đối tượng cụ thể nào.

| Placeholder Key | Nhãn (Label) | Ghi chú |
| :--- | :--- | :--- |
| `hdtd` | HĐTD | Số hợp đồng tín dụng |
| `ngay_hop_dong` | Ngày xác lập | Ngày ký kết các hợp đồng |
| `so_tien_vay` | Số tiền vay | Số tiền vay/hạn mức vay |
| `tong_gia_tri_tai_san` | Tổng giá trị tài sản | Tổng giá trị của các TSBĐ |
| `ho_ten` | Họ Tên | Tên khách hàng chính |
| `cccd` | CCCD/CC/Hộ Chiếu | Số căn cước công dân |

*Sử dụng:* `{{ so_tien_vay | format_currency }}`

---

## 3. Các Loại Hợp đồng Tùy chỉnh (Custom Contracts)
Hệ thống sử dụng các Object Types riêng để quản lý các loại hợp đồng khác nhau.

### Danh sách các loại hợp đồng:
- `CONTRACT_HDTC`: Hợp đồng thế chấp.
- `CONTRACT_HDTD_HM`: Hợp đồng tín dụng hạn mức.
- `CONTRACT_HDTD_TL`: Hợp đồng tín dụng từng lần.

### Cách truy xuất thông tin hợp đồng:
Bạn có thể sử dụng vòng lặp hoặc truy xuất trực tiếp nếu hợp đồng đó được gán vào hồ sơ.

| Placeholder Key | Nhãn | Loại đối tượng |
| :--- | :--- | :--- |
| `hdtc` | Số HĐTC | `CONTRACT_HDTC` |
| `ngay_ky` | Ngày ký | Tất cả hợp đồng |
| `gia_tri_hd` | Giá trị hợp đồng | Tất cả hợp đồng |

*Ví dụ truy xuất HĐTC đầu tiên:*
`{{ contract_hdtc_list[0].hdtc }} ký ngày {{ contract_hdtc_list[0].ngay_ky }}`

---

## 4. Danh sách Người liên quan (People)
Dữ liệu người dùng được gửi dưới dạng danh sách (List).

### Biến danh sách chính:
- `people`: Tất cả người trong hồ sơ.

#### Thuộc tính người (person):
`{{ p.ho_ten }}`, `{{ p.cccd }}`, `{{ p.dia_chi_thuong_tru }}`

---

## 5. Danh sách Tài sản (Assets)
Dữ liệu tài sản được gửi dưới dạng danh sách (List).

### Biến danh sách chính:
- `assets`: Tất cả tài sản trong hồ sơ.
- Phân loại: `REALESTATE`, `VEHICLE`, `SAVINGS`...

---

## 6. Các Bộ lọc (Filters) hỗ trợ
1. **Tiền tệ:** `{{ x | format_currency }}`
2. **Số thành chữ:** `{{ x | num2words }}`
3. **Ngày tháng:** `{{ x | dateformat('%d/%m/%Y') }}`
