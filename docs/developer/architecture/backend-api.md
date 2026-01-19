# Tài liệu API Backend

## Tổng quan

Backend của Vietbank Contract App được xây dựng với **Django** và **Django REST Framework (DRF)**. Nó cung cấp RESTful API cho xác thực người dùng, quản lý hồ sơ, tự động hóa tài liệu và các chức năng quản trị.

## Công nghệ Sử dụng

- **Framework**: Django 5.2.7
- **API**: Django REST Framework
- **Database**: SQLite (development) / PostgreSQL (production)
- **Authentication**: Token-based (DRF TokenAuthentication)
- **ORM**: Django ORM

## URL API Cơ bản

```
Development: http://127.0.0.1:8000/api/
Production: https://api.vietbank.com/api/
```

## Xác thực

### Xác thực Dựa trên Token

Tất cả endpoint yêu cầu xác thực cần token trong header `Authorization`:

```http
Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b
```

### Lấy Token

**Endpoint**: `POST /api/auth/login/`

**Request**:
```json
{
  "username": "user@example.com",
  "password": "password123"
}
```

**Response**:
```json
{
  "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b",
  "user": {
    "id": 1,
    "username": "user@example.com",
    "email": "user@example.com",
    "is_staff": false,
    "is_superuser": false,
    "profile": {
      "full_name": "Nguyễn Văn A",
      "phone": "0123456789",
      "workplace": "Trụ sở chính",
      "department": "IT"
    }
  }
}
```

## Endpoints Cốt lõi

### Quản lý Người dùng

#### Lấy Hồ sơ Người dùng Hiện tại
```http
GET /api/me/
Authorization: Token {token}
```

**Response**:
```json
{
  "id": 1,
  "username": "user@example.com",
  "email": "user@example.com",
  "profile": {
    "full_name": "Nguyễn Văn A",
    "phone": "0123456789",
    "workplace": "Trụ sở chính",
    "department": "IT"
  },
  "groups": ["soạn thảo"],
  "permissions": ["view_document", "create_document"]
}
```

#### Cập nhật Hồ sơ
```http
PATCH /api/me/
Authorization: Token {token}
Content-Type: application/json
```

**Request**:
```json
{
  "full_name": "Nguyễn Thị B",
  "email": "jane@example.com",
  "phone": "0987654321",
  "workplace": "Chi nhánh 1",
  "department": "Pháp chế"
}
```

#### Đổi Mật khẩu
```http
POST /api/change-password/
Authorization: Token {token}
Content-Type: application/json
```

**Request**:
```json
{
  "old_password": "oldpass123",
  "new_password": "newpass456"
}
```

**Response**:
```json
{
  "message": "Đổi mật khẩu thành công"
}
```

**Lỗi** (400):
```json
{
  "old_password": ["Mật khẩu không đúng"]
}
```

### Đăng ký Người dùng

#### Đăng ký User Mới
```http
POST /api/register/
Content-Type: application/json
```

**Request**:
```json
{
  "username": "newuser",
  "email": "newuser@example.com",
  "password": "password123",
  "full_name": "Người dùng mới",
  "phone": "0123456789",
  "workplace": "Trụ sở chính",
  "department": "IT"
}
```

**Response** (201):
```json
{
  "id": 2,
  "username": "newuser",
  "email": "newuser@example.com",
  "token": "abc123...",
  "groups": ["soạn thảo"]
}
```

**Gán tự động**: User mới sẽ tự động được thêm vào nhóm **"soạn thảo"**.

### Endpoints Admin

#### Danh sách Users (Chỉ Admin)
```http
GET /api/users/
Authorization: Token {admin_token}
```

**Response**:
```json
[
  {
    "id": 1,
    "username": "admin",
    "email": "admin@vietbank.com",
    "is_staff": true,
    "is_superuser": true,
    "profile": { ... },
    "groups": [1, 2],
    "permissions": ["all"]
  },
  ...
]
```

#### Tạo User (Chỉ Admin)
```http
POST /api/users/
Authorization: Token {admin_token}
Content-Type: application/json
```

#### Cập nhật User (Chỉ Admin)
```http
PUT /api/users/{id}/
Authorization: Token {admin_token}
Content-Type: application/json
```

#### Xóa User (Chỉ Admin)
```http
DELETE /api/users/{id}/
Authorization: Token {admin_token}
```

**Response** (204): Không có nội dung

### Nhóm & Quyền hạn

#### Danh sách Nhóm
```http
GET /api/user-groups/
Authorization: Token {token}
```

**Response**:
```json
[
  {
    "id": 1,
    "name": "soạn thảo",
    "permissions": ["view_document", "create_document"]
  },
  ...
]
```

#### Tạo Nhóm (Chỉ Admin)
```http
POST /api/user-groups/
Authorization: Token {admin_token}
Content-Type: application/json
```

**Request**:
```json
{
  "name": "kế toán",
  "permissions": [1, 2, 3]
}
```

### Nhật ký Kiểm toán (Audit Logs)

#### Danh sách Nhật ký (Chỉ Admin)
```http
GET /api/audit-logs/
Authorization: Token {admin_token}
```

**Tham số Query**:
- `user`: Lọc theo user ID
- `action`: Lọc theo hành động (CREATE, UPDATE, DELETE)
- `limit`: Số kết quả (mặc định: 100)

**Response**:
```json
[
  {
    "id": 1,
    "user": "admin",
    "action": "UPDATE",
    "object_type": "User",
    "object_id": 5,
    "changes": {
      "email": ["old@example.com", "new@example.com"]
    },
    "timestamp": "2026-01-18T10:30:00Z"
  },
  ...
]
```

## Models Dữ liệu

### User Model
```python
class User(AbstractUser):
    email = EmailField(unique=True)
    is_staff = BooleanField(default=False)
    is_superuser = BooleanField(default=False)
    groups = ManyToManyField(Group)
    user_permissions = ManyToManyField(Permission)
```

### UserProfile Model
```python
class UserProfile(Model):
    user = OneToOneField(User, on_delete=CASCADE)
    full_name = CharField(max_length=255)
    phone = CharField(max_length=20, blank=True)
    workplace = CharField(max_length=255, blank=True)
    department = CharField(max_length=255, blank=True)
```

## Serializers

### RegistrationSerializer
```python
class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    full_name = serializers.CharField()
    
    def create(self, validated_data):
        # Tạo user
        user = User.objects.create_user(**validated_data)
        
        # Cập nhật profile
        user.profile.full_name = validated_data['full_name']
        user.profile.save()
        
        # Tự động gán nhóm "soạn thảo"
        try:
            draft_group = Group.objects.filter(name='soạn thảo').first()
            if draft_group:
                user.groups.add(draft_group)
        except Exception:
            pass
        
        return user
```

## Phân quyền & Ủy quyền

### Cấp độ Quyền hạn

1. **Superuser**: Bỏ qua tất cả kiểm tra quyền
2. **Staff**: Truy cập endpoints admin
3. **Quyền Nhóm**: Kế thừa từ nhóm
4. **Quyền User**: Quyền trực tiếp của user

### Kiểm tra Quyền hạn

```python
# Trong views
class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get_queryset(self):
        if self.request.user.is_superuser:
            return User.objects.all()
        return User.objects.filter(is_superuser=False)
```

## Xử lý Lỗi

### Response Lỗi Chuẩn

#### 400 Bad Request
```json
{
  "field_name": ["Thông báo lỗi"],
  "non_field_errors": ["Lỗi chung"]
}
```

#### 401 Unauthorized
```json
{
  "detail": "Chưa cung cấp thông tin xác thực."
}
```

#### 403 Forbidden
```json
{
  "detail": "Bạn không có quyền thực hiện hành động này."
}
```

#### 404 Not Found
```json
{
  "detail": "Không tìm thấy."
}
```

## Thực hành Tốt nhất

### 1. Luôn Dùng Serializers
```python
# Tốt
serializer = UserSerializer(data=request.data)
if serializer.is_valid():
    serializer.save()

# Không tốt
User.objects.create(**request.data)
```

### 2. Validate Input
```python
class UserSerializer(serializers.ModelSerializer):
    def validate_email(self, value):
        if not value.endswith('@vietbank.com'):
            raise serializers.ValidationError("Phải dùng email công ty")
        return value
```

### 3. Dùng Transactions
```python
from django.db import transaction

@transaction.atomic
def create_user_with_profile(data):
    user = User.objects.create(**data)
    UserProfile.objects.create(user=user, ...)
    return user
```

## Testing

### Unit Tests
```python
from django.test import TestCase

class UserAPITestCase(TestCase):
    def test_create_user(self):
        response = self.client.post('/api/users/', {
            'username': 'test',
            'email': 'test@example.com',
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 201)
```

## Deployment

### Biến Môi trường
```env
DEBUG=False
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@host:5432/dbname
ALLOWED_HOSTS=api.vietbank.com
```

### Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

## Tài nguyên

- **Django Docs**: https://docs.djangoproject.com/
- **DRF Docs**: https://www.django-rest-framework.org/
- **Tích hợp Frontend**: Xem `frontend-structure.md`
