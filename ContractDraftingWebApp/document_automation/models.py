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
    ENTITY_CHOICES = [
        ('PROFILE', 'Hồ sơ'),
        ('PERSON', 'Cá nhân'),
        ('ASSET', 'Tài sản'),
        ('SAVINGS', 'Sổ tiết kiệm'),
    ]
    name = models.CharField(max_length=255, verbose_name="Tên nhóm")
    slug = models.SlugField(max_length=100, unique=True, null=True, blank=True, verbose_name="Mã định danh (Slug)") # MỚI
    entity_type = models.CharField(
        max_length=20, 
        choices=ENTITY_CHOICES, 
        default='PROFILE',
        verbose_name="Đối tượng áp dụng"
    )
    layout_position = models.CharField(
        max_length=10,
        choices=[('LEFT', 'Cột Trái'), ('RIGHT', 'Cột Phải')],
        default='LEFT',
        verbose_name="Vị trí hiển thị"
    )
    order = models.IntegerField(default=0, verbose_name="Thứ tự hiển thị")
    note = models.TextField(blank=True, null=True, verbose_name="Ghi chú")
    allowed_forms = models.ManyToManyField(FormView, blank=True, related_name='groups', verbose_name="Hiển thị ở Form")
    allowed_object_types = models.ManyToManyField('MasterObjectType', blank=True, related_name='groups',
                                                  verbose_name="Loại Đối tượng áp dụng")  # MỚI
    
    # NEW: Link to MasterObjectType for categorization
    object_type = models.ForeignKey(
        'MasterObjectType',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='categorized_groups',
        verbose_name="Phân loại nhóm",
        help_text="Nhóm này dành cho loại đối tượng nào? Để trống = Thông tin chung (CORE)"
    )


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
    use_digit_grouping = models.BooleanField(default=False, verbose_name="Phân tách hàng nghìn (chuẩn vi-VN)")
    show_amount_in_words = models.BooleanField(default=False, verbose_name="Hiển thị số thành chữ (Frontend)")
    default_value = models.TextField(blank=True, null=True, verbose_name="Giá trị mặc định")
    allowed_forms = models.ManyToManyField(FormView, blank=True, related_name='fields', verbose_name="Hiển thị ở Form")
    allowed_object_types = models.ManyToManyField('MasterObjectType', blank=True, related_name='fields',
                                                  verbose_name="Loại Đối tượng áp dụng")  # MỚI
    note = models.TextField(blank=True, null=True, verbose_name="Ghi chú")

    def __str__(self):
        return f"{self.label} ({self.placeholder_key})"

    class Meta:
        verbose_name = "Trường Dữ liệu"
        verbose_name_plural = "Trường Dữ liệu"


# --- MỚI: Bảng Vai trò (Dynamic Role) ---
class Role(models.Model):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=100, unique=True, null=True, blank=True) # MỚI: Dùng để định danh trong template
    description = models.TextField(blank=True, null=True)
    
    # --- New Fields for Relations ---
    relation_type = models.CharField(
        max_length=50, 
        blank=True, 
        null=True, 
        verbose_name="Loại quan hệ tự động",
        help_text="Nếu Role này được chọn, hệ thống sẽ tự động gán quan hệ này (VD: OWNER)"
    )
    is_system = models.BooleanField(
        default=False, 
        verbose_name="Là hệ thống",
        help_text="Role quan trọng không được phép xóa"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Vai trò (Role)"
        verbose_name_plural = "Quản lý Vai trò"


# 2. Bảng Mẫu Tài liệu (ĐÃ BỔ SUNG LẠI)
class DocumentTemplate(models.Model):
    name = models.CharField(max_length=255, verbose_name="Tên mẫu")
    file = models.FileField(upload_to='doc_templates/', verbose_name="File mẫu (.docx)")
    department = models.CharField(max_length=100, blank=True, null=True, verbose_name="Bộ phận")
    description = models.TextField(blank=True, null=True, verbose_name="Ghi chú")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tải lên")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Mẫu Tài liệu"
        verbose_name_plural = "Mẫu Tài liệu"


# 3. Bảng Hồ sơ Vay
class LoanProfile(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Đang xử lý (Nháp)'),
        ('FINALIZED', 'Đã hoàn tất (Khóa)'),
    ]
    
    created_by_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=255, verbose_name="Tên hồ sơ", default="Hồ sơ mới")
    form_view = models.ForeignKey(FormView, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Cấu hình Form")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT', verbose_name="Trạng thái")
    lock_password = models.CharField(max_length=100, blank=True, null=True, verbose_name="Mật khẩu khóa (Dev)")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Hồ sơ Vay"
        verbose_name_plural = "Hồ sơ Vay"




# --- UNIVERSAL ENTITY ARCHITECTURE (New) ---

# 5.b Loại Đối tượng (Dynamic)
class MasterObjectType(models.Model):
    DISPLAY_MODE_CHOICES = [
        ('ASSET_LIST', 'Gom trong danh sách Tài sản'),
        ('DEDICATED_SECTION', 'Hiển thị khu vực riêng'),
    ]
    
    code = models.CharField(max_length=50, unique=True, verbose_name="Mã loại (VD: PERSON)")
    name = models.CharField(max_length=100, verbose_name="Tên hiển thị (VD: Cá nhân)")
    description = models.TextField(blank=True, null=True, verbose_name="Mô tả")
    is_system = models.BooleanField(default=False, verbose_name="Là hệ thống (Không xóa)")
    identity_field_key = models.CharField(max_length=100, blank=True, null=True, verbose_name="Trường định danh (key)", help_text="Placeholder key của trường dùng để làm tên định danh (VD: ho_ten, bien_so_xe)")
    dynamic_summary_template = models.CharField(max_length=255, blank=True, null=True, verbose_name="Mẫu hiển thị tóm tắt", help_text="Mẫu để hiển thị thông tin bổ sung (VD: CCCD: {cccd})")
    form_display_mode = models.CharField(
        max_length=30, 
        choices=DISPLAY_MODE_CHOICES, 
        default='ASSET_LIST',
        verbose_name="Chế độ hiển thị Form",
        help_text="Chọn cách đối tượng này hiển thị trong hồ sơ vay"
    )
    layout_position = models.CharField(
        max_length=10,
        choices=[('LEFT', 'Cột Trái'), ('RIGHT', 'Cột Phải')],
        default='LEFT',
        verbose_name="Vị trí hiển thị"
    )
    allow_relations = models.BooleanField(
        default=True,
        verbose_name="Cho phép gán liên kết",
        help_text="Nếu tắt, đối tượng này sẽ không xuất hiện trong danh sách gán quan hệ và không hiển thị khu vực 'Các liên kết liên quan'"
    )
    order = models.IntegerField(default=0, verbose_name="Thứ tự hiển thị")
    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Loại Đối tượng"
        verbose_name_plural = "Các Loại Đối tượng"


# 6. MasterObject - Universal Entity Container
class MasterObject(models.Model):
    object_type = models.CharField(
        max_length=20,
        # choices=OBJECT_TYPE_CHOICES, # Removed hardcoded choices to allow dynamic types
        verbose_name="Loại đối tượng"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Ngày tạo")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Ngày cập nhật")
    last_updated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Người cập nhật")

    def __str__(self):
        # Fallback string representation
        return self.display_name

    @property
    def display_name(self):
        """Ưu tiên trả về Tên (Mã định danh) để hiển thị thân thiện trên toàn hệ thống"""
        try:
            # 1. Tìm các trường tiềm năng là "Tên"
            name_keys = ['ho_ten', 'ten_tai_san', 'ten_doi_tuong', 'ten_khach_hang', 'name', 'full_name']
            name_fv = self.fieldvalue_set.filter(
                field__placeholder_key__in=name_keys, 
                loan_profile__isnull=True
            ).first()
            name_val = name_fv.value if name_fv else ""
            
            # 2. Lấy giá trị định danh từ cấu hình identity_field_key của loại
            from .models import MasterObjectType
            cfg = MasterObjectType.objects.filter(code=self.object_type).first()
            id_key = cfg.identity_field_key if cfg else None
            
            id_val = ""
            if id_key:
                id_fv = self.fieldvalue_set.filter(
                    field__placeholder_key=id_key, 
                    loan_profile__isnull=True
                ).first()
                id_val = id_fv.value if id_fv else ""
                
            # 3. Kết hợp kết quả: Tên (Mã)
            if name_val and id_val and name_val != id_val:
                return f"{name_val} ({id_val})"
            if name_val:
                return name_val
            if id_val:
                return id_val
            
            # 4. Fallback cuối cùng
            return f"{self.object_type} #{self.id}"
        except Exception:
            return f"Object #{self.id}"


    class Meta:
        verbose_name = "Đối tượng"
        verbose_name_plural = "Các đối tượng"
        indexes = [
            models.Index(fields=['object_type']),
        ]


# 7. Liên kết Hồ sơ - Đối tượng (Universal)
class LoanProfileObjectLink(models.Model):
    loan_profile = models.ForeignKey(LoanProfile, on_delete=models.CASCADE, related_name='object_links')
    master_object = models.ForeignKey(MasterObject, on_delete=models.CASCADE, related_name='profile_links')
    roles = models.JSONField(default=list, blank=True, verbose_name="Vai trò")

    class Meta:
        unique_together = ('loan_profile', 'master_object')
        verbose_name = "Liên kết Hồ sơ và Đối tượng"
        verbose_name_plural = "Liên kết Hồ sơ và Đối tượng"
        indexes = [
            models.Index(fields=['loan_profile', 'master_object']),
        ]

    def __str__(self):
        roles_str = ', '.join(self.roles) if self.roles else 'Không có vai trò'
        return f"{self.master_object} -> {self.loan_profile.name} ({roles_str})"


# 6. Bảng Giá trị của các Trường - Universal
class FieldValue(models.Model):
    loan_profile = models.ForeignKey(LoanProfile, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Hồ sơ")
    master_object = models.ForeignKey(MasterObject, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Đối tượng")
    field = models.ForeignKey(Field, on_delete=models.CASCADE, verbose_name="Trường")
    value = models.TextField(verbose_name="Giá trị thực tế")

    class Meta:
        # Unique constraint: (profile, object, field) - cho phép null ở cả profile và object
        unique_together = ('loan_profile', 'master_object', 'field')
        verbose_name = "Giá trị"
        verbose_name_plural = "Các giá trị"
        indexes = [
            models.Index(fields=['loan_profile']),
            models.Index(fields=['master_object']),
        ]

    def __str__(self):
        return f"{self.field.placeholder_key}: {self.value}"

# --- MỚI: Bảng phụ cho User để lưu thông tin chi tiết ---
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    full_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Họ và tên")
    phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Số điện thoại")
    workplace = models.CharField(max_length=255, blank=True, null=True, verbose_name="Nơi làm việc")
    department = models.CharField(max_length=255, blank=True, null=True, verbose_name="Phòng ban")
    note = models.TextField(blank=True, null=True, verbose_name="Ghi chú thêm")

    def __str__(self):
        return f"Profile of {self.user.username}"


# --- MỚI: Bảng Nhật ký tác động (Audit Log) ---
class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('LOGIN', 'Đăng nhập'),
        ('LOGOUT', 'Đăng xuất'),
        ('CREATE', 'Tạo mới'),
        ('UPDATE', 'Cập nhật'),
        ('DELETE', 'Xóa'),
    ]
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Người thực hiện")
    action = models.CharField(max_length=20, choices=ACTION_CHOICES, verbose_name="Hành động")
    target_model = models.CharField(max_length=100, verbose_name="Đối tượng tác động")
    target_id = models.CharField(max_length=50, blank=True, null=True, verbose_name="ID đối tượng")
    details = models.TextField(blank=True, null=True, verbose_name="Chi tiết thay đổi")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="Thời gian")

    class Meta:
        verbose_name = "Nhật ký tác động"
        verbose_name_plural = "Nhật ký tác động"
        ordering = ['-timestamp']

    def __str__(self):
        user_str = self.user.username if self.user else "System/Unknown"
        return f"{user_str} - {self.action} on {self.target_model}"


# 8. Quan hệ Trực tiếp giữa các Đối tượng (Master Relations)
class MasterObjectRelation(models.Model):
    source_object = models.ForeignKey(
        MasterObject, 
        on_delete=models.CASCADE, 
        related_name='relations_as_source',
        verbose_name="Đối tượng nguồn"
    )
    target_object = models.ForeignKey(
        MasterObject, 
        on_delete=models.CASCADE, 
        related_name='relations_as_target',
        verbose_name="Đối tượng đích"
    )
    relation_type = models.CharField(max_length=50, verbose_name="Loại quan hệ") # VD: OWNER
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('source_object', 'target_object', 'relation_type')
        verbose_name = "Quan hệ Đối tượng"
        verbose_name_plural = "Quan hệ Đối tượng"
        indexes = [
            models.Index(fields=['source_object']),
            models.Index(fields=['target_object']),
        ]

    def __str__(self):
        return f"{self.source_object} --{self.relation_type}--> {self.target_object}"

# --- MỚI: Signal để tự động tạo UserProfile khi tạo User ---
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()