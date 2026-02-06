---
trigger: always_on
---

Hệ thống sử dụng các modal để hiển thị lỗi.

Kiểm tra nếu lỗi là 403 (Forbidden), chỉ sử dụng thông báo Toàn cục (Global) để tránh chồng chéo.

Thêm cơ chế chống lặp (debounce/throttle) hoặc lưu trạng thái "đang hiển thị" để không hiện nhiều thông báo cùng lúc cho cùng một loại lỗi trong thời gian ngắn.

Ưu tiên Global Modal và chỉ dùng Local Modal làm fallback nếu không có global handler.