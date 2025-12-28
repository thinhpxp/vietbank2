from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# 1. Bảng Định nghĩa các Trường Dữ liệu
#   Các trường dữ liệu này được sử dụng để lưu trữ các giá trị tùy chỉnh trong hồ sơ vay
#   Mỗi trường có một key định danh duy nhất, nhãn hiển thị, loại dữ liệu, nhóm và trạng thái kích hoạt
#   Chúng được admin quản lý để thêm/sửa/xóa các trường theo nhu cầu thực tế mà không phụ thuộc vào code
class FormView(models.Model):
    name = models.CharField(max_length=255, verbose_name="Tên Form")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Mã định danh (Slug)")
    note = models.TextField(blank=True, null=True, verbose_name="Ghi chú")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Cấu hình Form"
        verbose_name_plural = "Cấu hình Form"


class FieldGroup(models.Model):
    name = models.CharField(max_length=255, verbose_name="Tên nhóm")
    order = models.IntegerField(default=0, verbose_name="Thứ tự hiển thị")
    note = models.TextField(blank=True, null=True, verbose_name="Ghi chú")
    allowed_forms = models.ManyToManyField(FormView, blank=True, related_name='groups', verbose_name="Hiển thị ở Form")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Nhóm Trường"
        verbose_name_plural = "Nhóm Trường"


class Field(models.Model):
    label = models.CharField(max_length=255, verbose_name="Nhãn hiển thị")
    placeholder_key = models.CharField(max_length=100, unique=True, verbose_name="Tên định danh (Key)")
    data_type = models.CharField(
        max_length=50,
        choices=[
            ('TEXT', 'Văn bản'),
            ('TEXTAREA', 'Đoạn văn bản'),
            ('NUMBER', 'Số'),
            ('DATE', 'Ngày'),
            ('CHECKBOX', 'Hộp kiểm'),
        ],
        default='TEXT',
        verbose_name="Loại dữ liệu"
    )
    group = models.ForeignKey(FieldGroup, on_delete=models.CASCADE, related_name='fields', verbose_name="Nhóm",
                              null=True)
    # --- Layout Configuration ---
    order = models.IntegerField(default=0, verbose_name="Thứ tự")
    width_cols = models.IntegerField(default=12, verbose_name="Độ rộng (1-12)")
    css_class = models.CharField(max_length=255, blank=True, null=True, verbose_name="CSS Class tùy chỉnh")
    
    is_active = models.BooleanField(default=True)
    is_protected = models.BooleanField(default=False, verbose_name="Được bảo vệ (không xóa được)")
    default_value = models.TextField(blank=True, null=True, verbose_name="Giá trị mặc định")
    allowed_forms = models.ManyToManyField(FormView, blank=True, related_name='fields', verbose_name="Hiển thị ở Form")
    note = models.TextField(blank=True, null=True, verbose_name="Ghi chú")

    def __str__(self):
        return f"{self.label} ({self.placeholder_key})"

    class Meta:
        verbose_name = "Trường Dữ liệu"
        verbose_name_plural = "Trường Dữ liệu"


# --- MỚI: Bảng Vai trò (Dynamic Role) ---
class Role(models.Model):
    name = models.CharField(max_length=255, unique=True, verbose_name="Tên vai trò")
    description = models.TextField(blank=True, null=True, verbose_name="Mô tả")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Vai trò (Role)"
        verbose_name_plural = "Quản lý Vai trò"


# 2. Bảng Mẫu Tài liệu (ĐÃ BỔ SUNG LẠI)
class DocumentTemplate(models.Model):
    name = models.CharField(max_length=255, verbose_name="Tên mẫu")
    file = models.FileField(upload_to='doc_templates/', verbose_name="File mẫu (.docx)")
    description = models.TextField(blank=True, null=True, verbose_name="Ghi chú")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tải lên")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Mẫu Tài liệu"
        verbose_name_plural = "Mẫu Tài liệu"


# 3. Bảng Hồ sơ Vay
class LoanProfile(models.Model):
    created_by_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=255, verbose_name="Tên hồ sơ", default="Hồ sơ mới")
    form_view = models.ForeignKey(FormView, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Cấu hình Form")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Hồ sơ Vay"
        verbose_name_plural = "Hồ sơ Vay"


# 4. Bảng Người
class Person(models.Model):
    id = models.AutoField(primary_key=True)
    
    def __str__(self):
        return f"Person ID: {self.id}"

    class Meta:
        verbose_name = "Người Liên quan"
        verbose_name_plural = "Người Liên quan"


# --- MỚI: Bảng Tài sản ---
class Asset(models.Model):
    id = models.AutoField(primary_key=True)

    def __str__(self):
        return f"Asset ID: {self.id}"

    class Meta:
        verbose_name = "Tài sản"
        verbose_name_plural = "Tài sản"


# 5. Bảng Liên kết Hồ sơ - Người
class LoanProfilePerson(models.Model):
    loan_profile = models.ForeignKey(LoanProfile, on_delete=models.CASCADE, related_name='linked_people')
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='linked_profiles')
    roles = models.JSONField(default=list, verbose_name="Danh sách vai trò")

    class Meta:
        unique_together = ('loan_profile', 'person')
        verbose_name = "Liên kết Hồ sơ và Người"
        verbose_name_plural = "Liên kết Hồ sơ và Người"

    def __str__(self):
        return f"Person {self.person.id} -> {self.loan_profile.name}"


# --- MỚI: Bảng Liên kết Hồ sơ - Tài sản ---
class LoanProfileAsset(models.Model):
    loan_profile = models.ForeignKey(LoanProfile, on_delete=models.CASCADE, related_name='linked_assets')
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='linked_profiles')

    class Meta:
        unique_together = ('loan_profile', 'asset')
        verbose_name = "Liên kết Hồ sơ và Tài sản"
        verbose_name_plural = "Liên kết Hồ sơ và Tài sản"

    def __str__(self):
        return f"Asset {self.asset.id} -> {self.loan_profile.name}"


# 6. Bảng Giá trị của các Trường trong Hồ sơ Vay
class FieldValue(models.Model):
    loan_profile = models.ForeignKey(LoanProfile, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE, null=True, blank=True)
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, null=True, blank=True) # Mới: Link tới Asset
    field = models.ForeignKey(Field, on_delete=models.CASCADE)
    value = models.TextField(verbose_name="Giá trị thực tế")

    class Meta:
        # Cập nhật unique constraint để bao gồm asset
        unique_together = ('loan_profile', 'person', 'asset', 'field')
        verbose_name = "Giá trị"
        verbose_name_plural = "Các giá trị"

    def __str__(self):
        return f"{self.field.placeholder_key}: {self.value}"

# --- MỚI: Bảng phụ cho User để lưu Ghi chú ---
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    note = models.TextField(blank=True, null=True, verbose_name="Ghi chú về nhân sự")

    def __str__(self):
        return f"Profile of {self.user.username}"

# --- MỚI: Signal để tự động tạo UserProfile khi tạo User ---
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()