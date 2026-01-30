# Hướng dẫn Phân tích: Gán quan hệ & Dẫn chiếu thông tin trong Template

Chức năng **"Gán quan hệ"** không chỉ là một liên kết mang tính hiển thị trên giao diện, mà là cơ chế cốt lõi để hệ thống tự động **Dẫn chiếu thông tin** (Cross-referencing) khi sinh các mẫu biểu hồ sơ (Hợp đồng, Tờ trình...).

---

## 1. Cơ chế hoạt động của Dẫn chiếu thông tin
Khi bạn gán một mối quan hệ giữa đối tượng A và đối tượng B (ví dụ: Ông A sở hữu Xe B), hệ thống sẽ:
1.  **Ghi nhận quan hệ:** Tạo một bản ghi trong cơ sở dữ liệu kết nối A và B với loại quan hệ (Relation Type).
2.  **Nhúng dữ liệu chéo:** Khi xuất file Word, toàn bộ thông tin của B sẽ được "nhúng" vào trong dữ liệu của A và ngược lại.

Điều này cho phép tài liệu của bạn có thể lấy thông tin "xuyên thấu" qua các đối tượng mà không cần nhập liệu lặp lại.

---

## 2. Các nhóm dẫn chiếu mặc định
Hệ thống phân chia các liên kết thành các "Ngăn chứa" (Buckets) để người dùng dễ dàng gọi ra trong template:

| Relation Type | Tên ngăn chứa trong Template | Ứng dụng dẫn chiếu |
| :--- | :--- | :--- |
| **OWNER / Generic** | `related_assets` | Từ Khách hàng dẫn chiếu đến các Tài sản họ sở hữu. |
| **OWNER / Generic** | `related_people` | Từ Tài sản dẫn chiếu ngược lại thông tin Chủ sở hữu. |
| **SECURES** | `secured_loan_contracts` | Từ HĐ Thế chấp dẫn chiếu đến HĐ Tín dụng được bảo đảm. |
| **SECURES** | `contracts_securing` | Từ HĐ Tín dụng dẫn chiếu đến danh sách các HĐ Bảo đảm. |
| **AMENDS** | `base_contracts` | Từ Phụ lục dẫn chiếu về thông tin Hợp đồng gốc. |

---

## 3. Cách sử dụng trong Template Word
Trong các mẫu file `.docx`, bạn sử dụng ngôn ngữ Jinja2 để truy xuất thông tin dẫn chiếu theo cú pháp:

### A. Lấy thông tin từ đối tượng được dẫn chiếu (Truy xuất trực tiếp)
Nếu bạn đang ở trong vòng lặp của **Tài sản**, và muốn lấy tên của **Chủ sở hữu** đầu tiên:
```jinja2
{{ asset.related_people[0].ho_ten }}
```

### B. Duyệt danh sách các đối tượng liên quan
Nếu một khách hàng có nhiều tài sản và bạn muốn liệt kê tất cả trong một bảng:
```jinja2
{% for ts in person.related_assets %}
- {{ ts.ten_tai_san }} (Biển số: {{ ts.bien_so }})
{% endfor %}
```

### C. Dẫn chiếu trong Hợp đồng bảo đảm
Để lấy ngày của Hợp đồng Tín dụng mà Hợp đồng Thế chấp này đang bảo đảm:
```jinja2
Căn cứ Hợp đồng tín dụng số {{ secured_loan_contracts[0].so_hd }} ký ngày {{ secured_loan_contracts[0].ngay_ky }}
```

---

## 4. Tự động hóa và Thủ công
*   **Tự động (Automatic Inference):** Hệ thống thông minh tự động gán quan hệ `OWNER` nếu bạn chọn một người vào hồ sơ với vai trò "Chủ tài sản". Bạn không cần vào nút "Gán quan hệ" mà thông tin vẫn tự động dẫn chiếu.
*   **Thủ công (Manual Assign):** Dùng đối với các quan hệ phức tạp, không theo quy luật (ví dụ: Tài sản này bảo đảm cho khoản vay của một người khác - thế chấp của bên thứ ba).

---
> [!TIP]
> **Kiểm tra dữ liệu dẫn chiếu:** Để biết chắc chắn một thông tin có được dẫn chiếu hay không, hãy nhìn vào phần **"🔗 Các liên kết liên quan"** ở cuối mỗi form nhập liệu. Nếu liên kết xuất hiện ở đó, bạn có thể gọi nó trong template.

---
*Tài liệu kỹ thuật - Vietbank*
