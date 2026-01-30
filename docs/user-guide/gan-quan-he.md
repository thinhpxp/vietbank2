# Hướng dẫn sử dụng: Tính năng "Gán quan hệ"

Tính năng **"Gán quan hệ"** cho phép người tạo hồ sơ thiết lập các mối liên kết chặt chẽ giữa các đối tượng (Cá nhân, Tài sản, Tổ chức...) trong cùng một hồ sơ vay. Việc gán quan hệ giúp hệ thống hiểu được logic của hồ sơ (ví dụ: ai là chủ tài sản, ai bảo đảm cho ai).

---

## 1. Khi nào cần gán quan hệ?
Bạn sử dụng tính năng này khi cần:
*   **Xác định chủ sở hữu:** Liên kết một *Cá nhân* với một *Tài sản* (loại OWNER).
*   **Xác định bảo đảm:** Liên kết một *Tài sản* với một *Khoản vay/Cá nhân* (loại SECURES).
*   **Dẫn chiếu thông tin:** Liên kết các đối tượng có liên quan về mặt pháp lý (loại REFERENCES).

---

## 2. Các bước thực hiện
Để gán quan hệ, bạn thực hiện theo các bước sau:

1.  **Mở mẫu nhập liệu:** Mở form chi tiết của một đối tượng (ví dụ: Click vào nút "Sửa" một khách hàng hoặc tài sản trong hồ sơ).
2.  **Tìm khu vực Liên kết:** Cuộn xuống cuối form, bạn sẽ thấy khu vực **🔗 Các liên kết liên quan**.
3.  **Nhấn nút Gán:** Nhấn vào nút **[+ Gán quan hệ]**.
4.  **Thiết lập thông tin trong cửa sổ (Modal):**
    *   **Loại quan hệ:** Chọn loại phù hợp (Sở hữu, Bảo đảm, Dẫn chiếu...).
    *   **Đối tượng liên kết:** Danh sách sẽ hiện ra các đối tượng khác đang có mặt trong hồ sơ này. Hãy click chọn đối tượng bạn muốn liên kết đến.
5.  **Xác nhận:** Nhấn **[Xác nhận gán]**.

---

## 3. Quản lý các liên kết đã gán
Sau khi gán thành công, liên kết sẽ hiển thị trong danh sách với các thông tin:
*   **Nhãn loại quan hệ:** Ví dụ: `OWNER`, `SECURES`.
*   **Hướng liên kết:** Hệ thống sẽ ghi rõ là liên kết "đến" hoặc "từ" đối tượng nào.
*   **Xóa liên kết:** Nếu gán nhầm, bạn có thể nhấn nút **[x]** màu đỏ bên cạnh liên kết để xóa. Việc xóa liên kết này chỉ gỡ bỏ mối quan hệ, không làm mất dữ liệu của các đối tượng liên quan.

---

## 4. Lưu ý quan trọng
> [!IMPORTANT]
> **Đối tượng đích:** Bạn chỉ có thể gán quan hệ với những đối tượng **đã được thêm vào hồ sơ hiện tại**. Nếu không thấy đối tượng cần tìm, hãy lưu hồ sơ và thêm đối tượng đó vào trước.

> [!TIP]
> **Tự động gán:** Ở một số vai trò đặc biệt (như Chủ tài sản), hệ thống có thể đã tự động thiết lập quan hệ khi bạn chọn đối tượng từ danh mục Master Data. Hãy kiểm tra danh sách liên kết trước khi thực hiện gán thủ công.

---
*Tài liệu hướng dẫn nội bộ - Vietbank*
