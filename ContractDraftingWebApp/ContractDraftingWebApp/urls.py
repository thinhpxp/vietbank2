from django.contrib import admin
from django.urls import path, include
from django.conf import settings # Import settings để cấu hình MEDIA
from django.conf.urls.static import static # Import static để phục vụ MEDIA
#from ContractDraftingWebApp.document_automation.views import home_view

# Import các View của Simple JWT
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView, # Tùy chọn, để kiểm tra tính hợp lệ của token
)

urlpatterns = [
    path('admin/', admin.site.urls),  # Dòng này phải đúng cho admin
    path('api/', include('document_automation.urls')),  # Dòng này phải đúng cho API của bạn

    # Các API của JWT
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
]

# Cấu hình để phục vụ file media trong môi trường dev
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)