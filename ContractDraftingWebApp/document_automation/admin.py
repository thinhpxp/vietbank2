from django.contrib import admin
# Import thêm FieldGroup
from .models import Field, LoanProfile, Person, LoanProfilePerson, FieldValue, DocumentTemplate, FieldGroup, Role

# --- 1. ĐĂNG KÝ MODEL MỚI: FIELD GROUP ---
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(FieldGroup)
class FieldGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    ordering = ('order',)

# --- 2. CẬP NHẬT FIELD ADMIN ---
@admin.register(Field)
class FieldAdmin(admin.ModelAdmin):
    # Sửa 'group_name' thành 'group'
    list_display = ('label', 'placeholder_key', 'data_type', 'group', 'is_active')
    # Sửa 'group_name' thành 'group'
    list_filter = ('data_type', 'group', 'is_active')
    search_fields = ('label', 'placeholder_key')

# --- 3. CẬP NHẬT CÁC MODEL KHÁC ---
@admin.register(LoanProfile)
class LoanProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by_user', 'created_at', 'updated_at')
    list_filter = ('created_by_user',)
    search_fields = ('name',)

@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_name', 'get_cccd')
    search_fields = ('id',)

    def get_name(self, obj):
        # Tìm FieldValue có key là 'ho_ten' gắn với Person này
        # Lưu ý: Có thể có nhiều giá trị nếu người này tham gia nhiều hồ sơ và giá trị khác nhau
        # Ở đây ta lấy giá trị mới nhất hoặc bất kỳ
        fv = obj.fieldvalue_set.filter(field__placeholder_key='ho_ten').last()
        return fv.value if fv else "-"
    get_name.short_description = "Họ và tên"

    def get_cccd(self, obj):
        fv = obj.fieldvalue_set.filter(field__placeholder_key='cccd_so').last()
        return fv.value if fv else "-"
    get_cccd.short_description = "Số CCCD"

@admin.register(LoanProfilePerson)
class LoanProfilePersonAdmin(admin.ModelAdmin):
    list_display = ('loan_profile', 'person', 'roles')
    list_filter = ('roles',) # Lưu ý: Filter theo JSONField có thể hạn chế tùy DB, nhưng cứ để tạm
    raw_id_fields = ('loan_profile', 'person')

@admin.register(FieldValue)
class FieldValueAdmin(admin.ModelAdmin):
    # Sửa 'field__group_name' thành 'field__group'
    list_display = ('loan_profile', 'person', 'field', 'value')
    list_filter = ('field__group', 'field__data_type')
    search_fields = ('value', 'loan_profile__name', 'field__label')
    raw_id_fields = ('loan_profile', 'person', 'field')

@admin.register(DocumentTemplate)
class DocumentTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'uploaded_at')
    search_fields = ('name',)