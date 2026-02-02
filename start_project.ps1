# Script khởi động nhanh dự án Vietbank (Chạy được từ Desktop)
$PROJECT_ROOT = "c:\Users\thinhpxp\Webapp_vietbank"

Write-Host "--- Đang khởi động Backend Django... ---" -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd \"$PROJECT_ROOT\ContractDraftingWebApp\"; .\venv\Scripts\Activate.ps1; python manage.py runserver"

Write-Host "--- Đang khởi động Frontend Vue... ---" -ForegroundColor Green
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd \"$PROJECT_ROOT\frontend\"; npm run serve"

Write-Host "`nĐã gửi lệnh khởi động. Vui lòng kiểm tra 2 cửa sổ mới mở." -ForegroundColor Yellow
Write-Host "Backend: http://localhost:8000/admin"
Write-Host "Frontend: http://localhost:8080/"

