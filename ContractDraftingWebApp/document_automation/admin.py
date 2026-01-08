from django.contrib import admin
# Import thêm FieldGroup, MasterObject, LoanProfileObjectLink
from .models import (
    Field, LoanProfile, FieldValue, 
    DocumentTemplate, FieldGroup, Role, MasterObject, LoanProfileObjectLink
)

# --- 1. ĐĂNG KÝ MODEL MỚI: FIELD GROUP ---
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)

@admin.register(FieldGroup)
class FieldGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'entity_type', 'order')
    list_filter = ('entity_type',)
    ordering = ('order',)

# --- UNIVERSAL ENTITY MODELS ---
@admin.register(MasterObject)
class MasterObjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'object_type', 'get_display_name', 'created_at', 'last_updated_by')
    list_filter = ('object_type', 'created_at')
    search_fields = ('id',)
    
    def get_display_name(self, obj):
        key = 'ho_ten' if obj.object_type == 'PERSON' else 'so_giay_chung_nhan'
        fv = obj.fieldvalue_set.filter(field__placeholder_key=key).first()
        return fv.value if fv else "-"
    get_display_name.short_description = "Tên hiển thị"

@admin.register(LoanProfileObjectLink)
class LoanProfileObjectLinkAdmin(admin.ModelAdmin):
    list_display = ('loan_profile', 'master_object', 'roles')
    list_filter = ('master_object__object_type',)
    raw_id_fields = ('loan_profile', 'master_object')

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


@admin.register(FieldValue)
class FieldValueAdmin(admin.ModelAdmin):
    # Updated to support both old (person/asset) and new (master_object) fields
    list_display = ('loan_profile', 'get_related_object', 'field', 'value')
    list_filter = ('field__group', 'field__data_type')
    search_fields = ('value', 'loan_profile__name', 'field__label')
    raw_id_fields = ('loan_profile', 'master_object', 'field')
    
    def get_related_object(self, obj):
        if obj.master_object:
            return f"MasterObject: {obj.master_object}"
        return "-"
    get_related_object.short_description = "Đối tượng liên quan"

@admin.register(DocumentTemplate)
class DocumentTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'uploaded_at')
    search_fields = ('name',)
