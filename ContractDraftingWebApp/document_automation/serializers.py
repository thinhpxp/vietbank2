# Serializers for Document Automation App
# Chức năng: Chuyển đổi dữ liệu mô hình thành định dạng JSON và ngược lại
# Có vai trò giống như một cầu nối giữa các mô hình dữ liệu và các API endpoints
from rest_framework import serializers
from django.contrib.auth.models import User, Group, Permission
from .models import (
    Field, FieldGroup, LoanProfile, FieldValue, DocumentTemplate, 
    Role, FormView, UserProfile, MasterObject, LoanProfileObjectLink, MasterObjectType,
    MasterObjectRelation, AuditLog, AdminNotification, NotificationRead, SystemConfig
)

import logging
logger = logging.getLogger(__name__)

# 0. Serializer cho Role (MỚI)
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'slug', 'description', 'relation_type', 'is_system']

# 0.0a Serializer cho Group và Permission (MỚI)
class PermissionSerializer(serializers.ModelSerializer):
    content_type = serializers.SerializerMethodField()

    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'content_type']

    def get_content_type(self, obj):
        if not obj.content_type:
            return "Khác"
        
        # Mapping tên Model sang Tiếng Việt thân thiện
        mapping = {
            'loanprofile': 'Hồ sơ vay',
            'loanprofileasset': 'Tài sản hồ sơ',
            'loanprofileperson': 'Người liên quan hồ sơ',
            'documenttemplate': 'Mẫu tài liệu',
            'field': 'Trường dữ liệu',
            'fieldgroup': 'Nhóm trường',
            'fieldvalue': 'Giá trị nhập liệu',
            'formview': 'Cấu hình giao diện',
            'masterobject': 'Đối tượng (Người/Tài sản)',
            'masterobjecttype': 'Loại đối tượng',
            'masterobjectrelation': 'Quan hệ đối tượng',
            'role': 'Vai trò',
            'user': 'Tài khoản người dùng',
            'group': 'Nhóm quyền',
            'userprofile': 'Thông tin mở rộng',
            'auditlog': 'Nhật ký hệ thống',
        }
        
        model_name = obj.content_type.model
        return mapping.get(model_name, f"Hệ thống: {model_name.capitalize()}")

class GroupSerializer(serializers.ModelSerializer):
    permissions_details = PermissionSerializer(source='permissions', many=True, read_only=True)
    class Meta:
        model = Group
        fields = ['id', 'name', 'permissions', 'permissions_details']

# 0.1 Serializer cho FormView (MỚI)
class FormViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormView
        fields = '__all__'

# 1.1 Serializer cho FieldGroup
class FieldGroupSerializer(serializers.ModelSerializer):
    allowed_object_type_codes = serializers.SerializerMethodField()

    def get_allowed_object_type_codes(self, obj):
        if obj.allowed_object_types.exists():
            return list(obj.allowed_object_types.values_list('code', flat=True))
        return []

    class Meta:
        model = FieldGroup
        fields = ['id', 'name', 'slug', 'order', 'note', 'allowed_forms', 'layout_position', 'allowed_object_types', 'allowed_object_type_codes', 'is_system']

# 1.2 Serializer cho Field
class FieldSerializer(serializers.ModelSerializer):
    # Hiển thị tên nhóm thay vì chỉ ID
    group_name = serializers.CharField(source='group.name', read_only=True)
    group_slug = serializers.CharField(source='group.slug', read_only=True)
    group_layout_position = serializers.CharField(source='group.layout_position', read_only=True)
    group_order = serializers.IntegerField(source='group.order', read_only=True)
    # Trả về danh sách ID (mặc định) để phục vụ UI Admin
    allowed_object_types = serializers.PrimaryKeyRelatedField(many=True, queryset=MasterObjectType.objects.all(), required=False)
    group_allowed_object_types = serializers.SerializerMethodField()
    
    # Các trường mới phục vụ Rendering (dùng mã Code thay vì ID)
    allowed_object_type_codes = serializers.SerializerMethodField()
    group_allowed_object_type_codes = serializers.SerializerMethodField()

    def get_group_allowed_object_types(self, obj):
        if obj.group and obj.group.allowed_object_types.exists():
            return list(obj.group.allowed_object_types.values_list('id', flat=True))
        return []

    def get_group_allowed_object_type_codes(self, obj):
        if obj.group and obj.group.allowed_object_types.exists():
            return list(obj.group.allowed_object_types.values_list('code', flat=True))
        return []
    
    def get_allowed_object_type_codes(self, obj):
        if obj.allowed_object_types.exists():
            return list(obj.allowed_object_types.values_list('code', flat=True))
        return []

    class Meta:
        model = Field
        fields = [
            'id', 'label', 'placeholder_key', 'data_type', 'group', 'group_name', 'group_slug', 'group_layout_position', 'group_order', 
            'group_allowed_object_types', 'group_allowed_object_type_codes', 'allowed_object_type_codes',
            'is_active', 'is_system', 'use_digit_grouping', 'show_amount_in_words', 'default_value', 'note', 
            'order', 'width_cols', 'css_class', 'allowed_forms', 'allowed_object_types'
        ]
        extra_kwargs = {
            'placeholder_key': {
                'error_messages': {
                    'unique': 'Key định danh này đã tồn tại trong hệ thống. Vui lòng chọn một mã khác.'
                }
            }
        }


# 2.1 Serializer cho User (Nâng cấp)
class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='profile.full_name', required=False, allow_blank=True, allow_null=True)
    phone = serializers.CharField(source='profile.phone', required=False, allow_blank=True, allow_null=True)
    workplace = serializers.CharField(source='profile.workplace', required=False, allow_blank=True, allow_null=True)
    department = serializers.CharField(source='profile.department', required=False, allow_blank=True, allow_null=True)
    note = serializers.CharField(source='profile.note', required=False, allow_blank=True, allow_null=True)
    # Chi nhánh: Dùng field thông thường để write, và to_representation để read
    branch_id = serializers.IntegerField(required=False, allow_null=True)
    branch_name = serializers.SerializerMethodField()
    groups_details = GroupSerializer(source='groups', many=True, read_only=True)
    permissions = serializers.SerializerMethodField()
    field_values = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_staff', 'is_superuser', 'is_active', 'password',
                  'full_name', 'phone', 'workplace', 'department', 'note',
                  'branch_id', 'branch_name',
                  'groups', 'groups_details', 'permissions', 'field_values']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False}
        }

    def get_permissions(self, obj):
        # Trả về danh sách codename của tất cả các quyền mà user có (bao gồm quyền từ Group)
        return list(obj.get_all_permissions())

    # (Đã chuyển branch_id thành IntegerField cho write/read)

    def get_branch_name(self, obj):
        try:
            branch = obj.profile.branch
            return branch.display_name if branch else None
        except Exception:
            return None

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        # Đảm bảo branch_id lấy đúng từ Profile khi trả về cho Frontend
        try:
            ret['branch_id'] = instance.profile.branch_id if instance.profile else None
        except Exception:
            ret['branch_id'] = None
        return ret

    @staticmethod
    def _apply_branch_to_profile(profile, branch_id):
        """Gán hoặc xóa chi nhánh cho UserProfile."""
        from .models import MasterObject
        if branch_id:
            try:
                branch = MasterObject.objects.get(id=int(branch_id), object_type='BRANCH')
                if branch.deleted_at is not None:
                    raise serializers.ValidationError({'branch_id': 'Chi nhánh này đã ngưng hoạt động, không thể chọn.'})
                profile.branch = branch
            except (MasterObject.DoesNotExist, ValueError, TypeError):
                pass
        else:
            profile.branch = None

    def create(self, validated_data):
        # Tách dữ liệu profile
        profile_data = validated_data.pop('profile', {})
        
        # Tách password
        password = validated_data.pop('password', None)
        
        # Tách groups
        groups = validated_data.pop('groups', [])
        
        # Tạo User
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
            
        # Gán groups
        if groups:
            user.groups.set(groups)
            
        # Cập nhật Profile (đã được tạo tự động qua Signal)
        profile, created = UserProfile.objects.get_or_create(user=user)
        for attr, value in profile_data.items():
            setattr(profile, attr, value)
        
        # Xử lý branch_id
        branch_id = validated_data.pop('branch_id', None)
        self._apply_branch_to_profile(profile, branch_id)
        
        profile.save()
        
        return user

    def get_field_values(self, obj):
        fvs = obj.dynamic_values.all()
        return {fv.field.placeholder_key: fv.value for fv in fvs}

    def update(self, instance, validated_data):
        # Tách dữ liệu profile (được source nén vào)
        profile_data = validated_data.pop('profile', {})
        
        # Tách field_values (nêu có gửi lên từ frontend)
        request = self.context.get('request')
        field_values_data = request.data.get('field_values', {}) if request else {}
        logger.info(f"User update: {instance.username}, field_values counts: {len(field_values_data)}")
        
        # Ngăn chặn đổi username nếu đã có
        validated_data.pop('username', None)
        
        # ... (đoạn code cũ giữ nguyên)
        # Cập nhật mật khẩu nếu có (thường Admin ít dùng qua update chung này)
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)

        # Cập nhật Group nếu có
        groups = validated_data.pop('groups', None)
        if groups is not None:
            instance.groups.set(groups)

        # Cập nhật các trường User chính
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Cập nhật Profile gắn kèm
        profile, created = UserProfile.objects.get_or_create(user=instance)
        for attr, value in profile_data.items():
            setattr(profile, attr, value)

        # Xử lý branch_id
        if 'branch_id' in validated_data:
            branch_id = validated_data.pop('branch_id')
            self._apply_branch_to_profile(profile, branch_id)

        profile.save()

        # Cập nhật FieldValues động cho User
        if field_values_data:
            for key, val in field_values_data.items():
                field = Field.objects.filter(placeholder_key=key, group__entity_type='USER_EXT').first()
                if field:
                    obj, created = FieldValue.objects.update_or_create(
                        user=instance,
                        field=field,
                        loan_profile=None,
                        master_object=None,
                        defaults={'value': str(val)}
                    )
                    logger.info(f"Saved {key}={val} for {instance.username}. Created: {created}")

        # Làm mới instance để serializer lấy được dữ liệu profile vừa lưu
        instance.refresh_from_db()
        return instance

# 2.2 Serializer cho Đăng ký (MỚI)
class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    full_name = serializers.CharField(required=True)
    phone = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    workplace = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    department = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    branch_id = serializers.IntegerField(required=False, allow_null=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'email', 'full_name', 'phone', 'workplace', 'department', 'branch_id']

    def create(self, validated_data):
        full_name = validated_data.pop('full_name')
        phone = validated_data.pop('phone', '')
        workplace = validated_data.pop('workplace', '')
        department = validated_data.pop('department', '')
        branch_id = validated_data.pop('branch_id', None)
        
        user = User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password'],
            email=validated_data.get('email', '')
        )
        
        # Profile sẽ được tạo tự động qua Signal, ta chỉ cần cập nhật
        user.profile.full_name = full_name
        user.profile.phone = phone
        user.profile.workplace = workplace
        user.profile.department = department
        
        if branch_id:
            from .models import MasterObject
            try:
                branch = MasterObject.objects.get(id=branch_id, object_type='BRANCH')
                if branch.deleted_at is not None:
                    raise serializers.ValidationError({'branch_id': 'Chi nhánh này đã ngưng hoạt động, không thể chọn.'})
                user.profile.branch = branch
            except MasterObject.DoesNotExist:
                pass
                
        user.profile.save()

        # Xử lý các trường động khi đăng ký
        field_values_data = self.initial_data.get('field_values', {})
        if field_values_data:
            for key, val in field_values_data.items():
                field = Field.objects.filter(placeholder_key=key, group__entity_type='USER_EXT').first()
                if field:
                    from .models import FieldValue
                    FieldValue.objects.create(
                        user=user,
                        field=field,
                        value=str(val)
                    )

        # Tự động gán nhóm "soạn thảo" nếu có
        try:
            draft_group = Group.objects.filter(name='soạn thảo').first()
            if draft_group:
                user.groups.add(draft_group)
        except Exception:
            pass # Tránh lỗi làm đứt quãng quá trình đăng ký nếu có vấn đề về Group
        
        return user

# 2.3 Serializer cho Đổi mật khẩu (MỚI)
class PasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Mật khẩu cũ không chính xác.")
        return value

# 5. Serializer cho FieldValue
class FieldValueSerializer(serializers.ModelSerializer):
    field = FieldSerializer(read_only=True)
    field_id = serializers.PrimaryKeyRelatedField(queryset=Field.objects.all(), source='field')

    class Meta:
        model = FieldValue
        fields = ['id', 'field', 'field_id', 'value', 'master_object', 'user']


# 6. Serializer cho LoanProfile
class LoanProfileSerializer(serializers.ModelSerializer):
    # Khai báo 3 trường tùy chỉnh mà Frontend cần
    field_values = serializers.SerializerMethodField()
    people = serializers.SerializerMethodField()
    attorneys = serializers.SerializerMethodField()
    assets = serializers.SerializerMethodField()
    form_view_slug = serializers.CharField(source='form_view.slug', read_only=True)
    form_view_name = serializers.CharField(source='form_view.name', read_only=True)

    # Hiển thị tên người tạo thay vì ID
    created_by_user_name = serializers.CharField(source='created_by_user.username', read_only=True)
    
    # MỚI: Tóm tắt các mã định danh để hiển thị ở danh sách (VD: Số HĐTC)
    search_identifiers = serializers.SerializerMethodField()
    is_deleted = serializers.SerializerMethodField()

    class Meta:
        model = LoanProfile
        fields = [
            'id', 'name', 'status', 'created_at', 'updated_at', 'created_by_user_name', 
            'field_values', 'people', 'attorneys', 'assets', 'object_sections', 'form_view_slug', 'form_view_name',
            'search_identifiers', 'deleted_at', 'delete_reason', 'is_deleted'
        ]
        read_only_fields = ['created_at', 'updated_at', 'deleted_at', 'is_deleted']

    def get_is_deleted(self, obj):
        return obj.deleted_at is not None

    # Logic 1: Gom các FieldValue chung
    def get_field_values(self, obj):
        # Lấy tất cả giá trị trường của hồ sơ này mà master_object là Null
        fvs = obj.fieldvalue_set.filter(master_object__isnull=True)
        return {fv.field.placeholder_key: fv.value for fv in fvs}

    def get_search_identifiers(self, obj):
        """
        Lấy các mã định danh quan trọng từ các đối tượng liên kết 
        dựa trên cấu hình identity_field_key của từng loại đối tượng.
        """
        # 1. Lấy tất cả identity_field_key đang được cấu hình trong DB
        identity_keys = list(MasterObjectType.objects.exclude(identity_field_key__isnull=True).exclude(identity_field_key='').values_list('identity_field_key', flat=True))
        
        if not identity_keys:
            return []
            
        # 2. Lấy giá trị của các trường này từ các MasterObject liên kết trực tiếp với Profile
        fvs = obj.fieldvalue_set.filter(
            field__placeholder_key__in=identity_keys,
            master_object__isnull=False
        ).values_list('value', flat=True)
        
        return list(set(filter(None, fvs)))

    # --- UNIVERSAL OBJECT SECTIONS (UOS) ---
    object_sections = serializers.SerializerMethodField()

    def get_object_sections(self, obj):
        """
        Gom nhóm các đối tượng theo object_type và cấu hình display_mode.
        Cấu trúc trả về: { "TYPE_CODE": [ { id, roles, individual_field_values }, ... ] }
        """
        sections = {}
        # Lấy tất cả các loại đối tượng để biết mode
        # type_configs = {t.code: t.form_display_mode for t in MasterObjectType.objects.all()}
        
        links = obj.object_links.all().select_related('master_object')
        
        for link in links:
            master = link.master_object
            t_code = master.object_type
            
            # Fetch values
            specific_fvs = FieldValue.objects.filter(loan_profile=obj, master_object=master)
            fv_dict = {fv.field.placeholder_key: fv.value for fv in specific_fvs}
            
            # Get whitelist metadata
            try:
                obj_type = MasterObjectType.objects.filter(code=t_code).first()
                is_restricted = obj_type.is_restricted if obj_type else False
                whitelist = [t.code for t in obj_type.allowed_relation_types.all()] if obj_type else []
                allow_relations = obj_type.allow_relations if obj_type else True
            except Exception:
                is_restricted = False
                whitelist = []
                allow_relations = True

            item_data = {
                "id": master.id,
                "roles": link.roles,
                "individual_field_values": fv_dict,
                "master_object": { 
                    "id": master.id, 
                    "object_type": t_code,
                    "is_restricted": is_restricted,
                    "allowed_relation_types_codes": whitelist,
                    "allow_relations": allow_relations,
                    "is_deleted": master.deleted_at is not None
                }
            }
            
            if t_code not in sections:
                sections[t_code] = []
            sections[t_code].append(item_data)
            
        return sections

    # Logic 2: Gom danh sách People (Duy trì cho Frontend cũ nếu cần)
    def get_people(self, obj):
        sections = self.get_object_sections(obj)
        return sections.get('PERSON', [])

    # Logic 2.5: Gom danh sách Attorneys (Duy trì cho Frontend cũ nếu cần)
    def get_attorneys(self, obj):
        sections = self.get_object_sections(obj)
        return sections.get('ATTORNEY', [])

    # Logic 3: Gom danh sách Assets (Dành cho các loại có mode ASSET_LIST)
    def get_assets(self, obj):
        # Lấy các loại được đánh dấu là ASSET_LIST
        asset_types = list(MasterObjectType.objects.filter(form_display_mode='ASSET_LIST').values_list('code', flat=True))
        # Loại trừ PERSON và ATTORNEY khỏi danh sách Assets mặc định nếu chúng chưa được gán mode
        if 'PERSON' in asset_types: asset_types.remove('PERSON')
        if 'ATTORNEY' in asset_types: asset_types.remove('ATTORNEY')
        
        sections = self.get_object_sections(obj)
        result = []
        for t_code, items in sections.items():
            if t_code in asset_types:
                # Format lại cho đúng cấu trúc asset cũ mà Frontend đang dùng
                for item in items:
                    result.append({
                        "id": item["id"],
                        "master_object": item["master_object"],
                        "asset_field_values": item["individual_field_values"], # Frontend cũ dùng key này
                        "roles": item["roles"]
                    })
        return result


# --- UNIVERSAL ENTITY SERIALIZERS (New Architecture) ---

class MasterObjectTypeSerializer(serializers.ModelSerializer):
    allowed_relation_types_codes = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='code',
        source='allowed_relation_types'
    )
    
    class Meta:
        model = MasterObjectType
        fields = [
            'id', 'code', 'name', 'description', 'is_system', 
            'identity_field_key', 'form_display_mode', 'dynamic_summary_template', 
            'allow_relations', 'is_restricted', 'allowed_relation_types', 'allowed_relation_types_codes',
            'order', 'layout_position'
        ]
        extra_kwargs = {
            'code': {
                'error_messages': {
                    'unique': 'Mã loại đối tượng này đã tồn tại. Vui lòng chọn một mã khác.'
                }
            }
        }

# --- HELPERS ---
def get_master_object_additional_info(obj, loan_profile_id=None):
    import re
    try:
        from .models import MasterObjectType, FieldValue
        obj_type_code = obj.object_type if hasattr(obj, 'object_type') else obj.get('object_type')
        obj_type_cfg = MasterObjectType.objects.filter(code=obj_type_code).first()
        template = obj_type_cfg.dynamic_summary_template if obj_type_cfg else ""
        if not template:
            return ""
        
        # 1. Lấy giá trị Master Data (mặc định)
        fvs_master = FieldValue.objects.filter(master_object=obj, loan_profile__isnull=True).select_related('field')
        fv_dict = {fv.field.placeholder_key: fv.value for fv in fvs_master}
        
        # 2. Nếu có loan_profile_id, lấy giá trị trong hồ sơ và ghi đè
        if loan_profile_id:
            fvs_profile = FieldValue.objects.filter(master_object=obj, loan_profile_id=loan_profile_id).select_related('field')
            for fv in fvs_profile:
                fv_dict[fv.field.placeholder_key] = fv.value
        
        # Thay thế {key} bằng value
        def replace_match(match):
            key = match.group(1)
            return str(fv_dict.get(key, f"{{{key}}}"))
        
        result = re.sub(r'\{(\w+)\}', replace_match, template)
        return result
    except Exception as e:
        print(f"DEBUG: Error in get_master_object_additional_info: {e}")
        return ""


class MasterObjectSerializer(serializers.ModelSerializer):
    """Universal serializer for all entity types (Person, Asset, Savings, etc.)"""
    display_name = serializers.SerializerMethodField()
    additional_info = serializers.SerializerMethodField()
    last_updated_by_name = serializers.CharField(source='last_updated_by.username', read_only=True)
    profiles_count = serializers.SerializerMethodField()
    field_values = serializers.SerializerMethodField()
    object_type_display = serializers.SerializerMethodField()
    allow_relations = serializers.SerializerMethodField()
    is_restricted = serializers.SerializerMethodField()
    allowed_relation_types_codes = serializers.SerializerMethodField()
    is_deleted = serializers.SerializerMethodField()

    class Meta:
        model = MasterObject
        fields = [
            'id', 'object_type', 'object_type_display', 'display_name', 'additional_info',
            'created_at', 'updated_at', 'last_updated_by_name', 
            'profiles_count', 'related_profiles', 'field_values', 
            'relations_out', 'relations_in', 'allow_relations',
            'is_restricted', 'allowed_relation_types_codes', 'is_deleted'
        ]
    
    # New fields for Relations and Profiles
    relations_out = serializers.SerializerMethodField()
    relations_in = serializers.SerializerMethodField()
    related_profiles = serializers.SerializerMethodField()

    def get_is_deleted(self, obj):
        return obj.deleted_at is not None

    def get_related_profiles(self, obj):
        """Lấy danh sách các hồ sơ vay mà đối tượng này tham gia"""
        links = obj.profile_links.all().select_related('loan_profile', 'loan_profile__form_view')
        return [
            {
                "id": link.loan_profile.id,
                "name": link.loan_profile.name,
                "form_name": link.loan_profile.form_view.name if link.loan_profile.form_view else "N/A",
                "status": link.loan_profile.status,
                "created_at": link.loan_profile.created_at,
                "roles": link.roles,
                "is_deleted": link.loan_profile.deleted_at is not None
            }
            for link in links
        ]


    def get_relations_out(self, obj):
        """Lấy tất cả các quan hệ mà đối tượng này là NGUỒN (Source) và hợp lệ theo Whitelist"""
        rels = obj.relations_as_source.all()
        valid_rels = []
        for rel in rels:
            if self._is_relation_valid(rel):
                valid_rels.append(rel)
        return MasterObjectRelationSerializer(valid_rels, many=True, context=self.context).data

    def get_relations_in(self, obj):
        """Lấy tất cả các quan hệ mà đối tượng này là ĐÍCH (Target) và hợp lệ theo Whitelist"""
        rels = obj.relations_as_target.all()
        valid_rels = []
        for rel in rels:
            if self._is_relation_valid(rel):
                valid_rels.append(rel)
        return MasterObjectRelationSerializer(valid_rels, many=True, context=self.context).data

    def _is_relation_valid(self, rel):
        """Helper kiểm tra tính hợp lệ của liên kết dựa trên Whitelist (Phase 10: Luôn hiện cả đối tượng đã xóa để làm mờ)"""
        try:
            # Phase 10: Không còn chặn dựa trên deleted_at tại đây để hỗ trợ "Liên kết lịch sử"
            # Tuy nhiên, nếu là ROOT thì có thể muốn filter khác? Không, cứ hiện hết để làm mờ.

            s_type_cfg = MasterObjectType.objects.filter(code=rel.source_object.object_type).first()
            t_type_cfg = MasterObjectType.objects.filter(code=rel.target_object.object_type).first()
            if not s_type_cfg or not t_type_cfg: return True

            # 1. Kiểm tra từ phía Source
            if s_type_cfg.is_restricted or s_type_cfg.allowed_relation_types.exists():
                if not s_type_cfg.allowed_relation_types.filter(code=t_type_cfg.code).exists():
                    return False
            
            # 2. Kiểm tra từ phía Target
            if t_type_cfg.is_restricted or t_type_cfg.allowed_relation_types.exists():
                if not t_type_cfg.allowed_relation_types.filter(code=s_type_cfg.code).exists():
                    return False
            
            return True
        except: return True

    def get_additional_info(self, obj):
        loan_profile_id = self.context.get('loan_profile_id')
        if not loan_profile_id and 'request' in self.context:
            loan_profile_id = self.context['request'].query_params.get('loan_profile_id')
        return get_master_object_additional_info(obj, loan_profile_id=loan_profile_id)

    def get_display_name(self, obj):
        """Sử dụng thuộc tính display_name đã được định nghĩa trong Model"""
        return obj.display_name


    
    def get_object_type_display(self, obj):
        """Get display name for object type from MasterObjectType"""
        try:
            obj_type = MasterObjectType.objects.get(code=obj.object_type)
            return obj_type.name
        except MasterObjectType.DoesNotExist:
            return obj.object_type

    def get_profiles_count(self, obj):
        return obj.profile_links.count()

    def get_field_values(self, obj):
        """Return all canonical field values for this object, prioritizing profile context"""
        from .models import FieldValue
        
        # 1. Master Data
        fvs_master = FieldValue.objects.filter(master_object=obj, loan_profile__isnull=True).select_related('field')
        fv_dict = {fv.field.placeholder_key: fv.value for fv in fvs_master}
        
        # 2. Profile Context
        loan_profile_id = self.context.get('loan_profile_id')
        if not loan_profile_id and 'request' in self.context:
            loan_profile_id = self.context['request'].query_params.get('loan_profile_id')
            
        if loan_profile_id:
            fvs_profile = FieldValue.objects.filter(master_object=obj, loan_profile_id=loan_profile_id).select_related('field')
            for fv in fvs_profile:
                fv_dict[fv.field.placeholder_key] = fv.value
                
        return fv_dict

    def get_allow_relations(self, obj):
        try:
            from .models import MasterObjectType
            obj_type = MasterObjectType.objects.filter(code=obj.object_type).first()
            return obj_type.allow_relations if obj_type else True
        except Exception:
            return True

    def get_is_restricted(self, obj):
        try:
            from .models import MasterObjectType
            obj_type = MasterObjectType.objects.filter(code=obj.object_type).first()
            return obj_type.is_restricted if obj_type else False
        except Exception:
            return False

    def get_allowed_relation_types_codes(self, obj):
        try:
            from .models import MasterObjectType
            obj_type = MasterObjectType.objects.filter(code=obj.object_type).first()
            if obj_type:
                return [t.code for t in obj_type.allowed_relation_types.all()]
            return []
        except Exception:
            return []

class MasterObjectLiteSerializer(serializers.ModelSerializer):
    """Serializer rút gọn cho tìm kiếm, tối ưu payload"""
    display_name = serializers.CharField(read_only=True)
    additional_info = serializers.SerializerMethodField()
    object_type_display = serializers.SerializerMethodField()
    field_values = serializers.SerializerMethodField()
    allow_relations = serializers.SerializerMethodField()
    is_restricted = serializers.SerializerMethodField()
    allowed_relation_types_codes = serializers.SerializerMethodField()
    is_deleted = serializers.SerializerMethodField()
    last_updated_by_name = serializers.CharField(source='last_updated_by.username', read_only=True)

    class Meta:
        model = MasterObject
        fields = [
            'id', 'object_type', 'object_type_display', 'display_name', 
            'additional_info', 'field_values', 'allow_relations',
            'is_restricted', 'allowed_relation_types_codes',
            'deleted_at', 'is_deleted',
            'created_at', 'updated_at', 'last_updated_by_name'
        ]

    def get_allow_relations(self, obj):
        try:
            from .models import MasterObjectType
            obj_type = MasterObjectType.objects.filter(code=obj.object_type).first()
            return obj_type.allow_relations if obj_type else True
        except Exception:
            return True

    def get_is_restricted(self, obj):
        try:
            from .models import MasterObjectType
            obj_type = MasterObjectType.objects.filter(code=obj.object_type).first()
            return obj_type.is_restricted if obj_type else False
        except Exception:
            return False

    def get_allowed_relation_types_codes(self, obj):
        try:
            from .models import MasterObjectType
            obj_type = MasterObjectType.objects.filter(code=obj.object_type).first()
            if obj_type:
                return [t.code for t in obj_type.allowed_relation_types.all()]
            return []
        except Exception:
            return []

    def get_is_deleted(self, obj):
        return obj.deleted_at is not None

    def get_additional_info(self, obj):
        loan_profile_id = self.context.get('loan_profile_id')
        if not loan_profile_id and 'request' in self.context:
            loan_profile_id = self.context['request'].query_params.get('loan_profile_id')
        return get_master_object_additional_info(obj, loan_profile_id=loan_profile_id)

    def get_object_type_display(self, obj):
        try:
            return MasterObjectType.objects.get(code=obj.object_type).name
        except:
            return obj.object_type

    def get_field_values(self, obj):
        """Return all canonical field values for this object, prioritizing profile context"""
        from .models import FieldValue
        
        # 1. Master Data
        fvs_master = FieldValue.objects.filter(master_object=obj, loan_profile__isnull=True).select_related('field')
        fv_dict = {fv.field.placeholder_key: fv.value for fv in fvs_master}
        
        # 2. Profile Context
        loan_profile_id = self.context.get('loan_profile_id')
        if not loan_profile_id and 'request' in self.context:
            loan_profile_id = self.context['request'].query_params.get('loan_profile_id')
            
        if loan_profile_id:
            fvs_profile = FieldValue.objects.filter(master_object=obj, loan_profile_id=loan_profile_id).select_related('field')
            for fv in fvs_profile:
                fv_dict[fv.field.placeholder_key] = fv.value
                
        return fv_dict



# 8. Serializer cho Relation (MỚI)
class MasterObjectRelationSerializer(serializers.ModelSerializer):
    source_name = serializers.CharField(source='source_object.display_name', read_only=True)
    target_name = serializers.CharField(source='target_object.display_name', read_only=True)
    target_type = serializers.CharField(source='target_object.object_type', read_only=True)
    source_type = serializers.CharField(source='source_object.object_type', read_only=True)
    
    source_additional_info = serializers.SerializerMethodField()
    target_additional_info = serializers.SerializerMethodField()
    source_is_restricted = serializers.SerializerMethodField()
    target_is_restricted = serializers.SerializerMethodField()
    source_allowed_relation_types_codes = serializers.SerializerMethodField()
    target_allowed_relation_types_codes = serializers.SerializerMethodField()
    
    # Phase 10: Thêm thông tin trạng thái xóa
    source_is_deleted = serializers.SerializerMethodField()
    target_is_deleted = serializers.SerializerMethodField()

    class Meta:
        model = MasterObjectRelation
        fields = ['id', 'source_object', 'target_object', 'relation_type', 'created_at', 
                  'source_name', 'target_name', 'target_type', 'source_type',
                  'source_additional_info', 'target_additional_info',
                  'source_is_deleted', 'target_is_deleted',
                  'source_is_restricted', 'target_is_restricted',
                  'source_allowed_relation_types_codes', 'target_allowed_relation_types_codes']

    def get_source_is_deleted(self, obj):
        return obj.source_object.deleted_at is not None

    def get_target_is_deleted(self, obj):
        return obj.target_object.deleted_at is not None

    def get_source_additional_info(self, obj):
        loan_profile_id = self.context.get('loan_profile_id')
        if not loan_profile_id and 'request' in self.context:
            loan_profile_id = self.context['request'].query_params.get('loan_profile_id')
        return get_master_object_additional_info(obj.source_object, loan_profile_id=loan_profile_id)

    def get_target_additional_info(self, obj):
        loan_profile_id = self.context.get('loan_profile_id')
        if not loan_profile_id and 'request' in self.context:
            loan_profile_id = self.context['request'].query_params.get('loan_profile_id')
        return get_master_object_additional_info(obj.target_object, loan_profile_id=loan_profile_id)

    def get_source_is_restricted(self, obj):
        try:
            from .models import MasterObjectType
            cfg = MasterObjectType.objects.filter(code=obj.source_object.object_type).first()
            return cfg.is_restricted if cfg else False
        except: return False

    def get_target_is_restricted(self, obj):
        try:
            from .models import MasterObjectType
            cfg = MasterObjectType.objects.filter(code=obj.target_object.object_type).first()
            return cfg.is_restricted if cfg else False
        except: return False

    def get_source_allowed_relation_types_codes(self, obj):
        try:
            from .models import MasterObjectType
            obj_type = MasterObjectType.objects.filter(code=obj.source_object.object_type).first()
            if obj_type:
                return [t.code for t in obj_type.allowed_relation_types.all()]
            return []
        except: return []

    def get_target_allowed_relation_types_codes(self, obj):
        try:
            from .models import MasterObjectType
            obj_type = MasterObjectType.objects.filter(code=obj.target_object.object_type).first()
            if obj_type:
                return [t.code for t in obj_type.allowed_relation_types.all()]
            return []
        except: return []


class LoanProfileObjectLinkSerializer(serializers.ModelSerializer):
    """Serializer for profile-object links with roles"""
    object = MasterObjectSerializer(source='master_object', read_only=True)
    master_object_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = LoanProfileObjectLink
        fields = ['id', 'loan_profile', 'master_object_id', 'object', 'roles']

# 9. Serializer cho Audit Log (MỚI)
class SimpleUserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='profile.full_name', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'full_name']

class AuditLogSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.username', read_only=True)
    user_full_name = serializers.CharField(source='user.profile.full_name', read_only=True)
    # Use SimpleUserSerializer to avoid performance overhead of full UserSerializer
    user_details = SimpleUserSerializer(source='user', read_only=True)

    class Meta:
        model = AuditLog
        fields = '__all__'


# Serializer cho DocumentTemplate (MỚI - cho Batch Export)
class DocumentTemplateSerializer(serializers.ModelSerializer):
    # Read-only fields để hiển thị thông tin loop_object_type
    loop_object_type_code = serializers.CharField(source='loop_object_type.code', read_only=True, allow_null=True)
    loop_object_type_name = serializers.CharField(source='loop_object_type.name', read_only=True, allow_null=True)
    
    class Meta:
        model = DocumentTemplate
        fields = ['id', 'name', 'file', 'department', 'description', 'uploaded_at', 
                  'loop_object_type', 'loop_object_type_code', 'loop_object_type_name']
        read_only_fields = ['uploaded_at']

# 10. Serializers cho Notification System (MỚI)
class AdminNotificationSerializer(serializers.ModelSerializer):
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    is_read = serializers.SerializerMethodField()

    class Meta:
        model = AdminNotification
        fields = ['id', 'title', 'content', 'type', 'is_active', 'expires_at', 'created_at', 'created_by_name', 'is_read']

    def get_is_read(self, obj):
        user = self.context.get('request').user if 'request' in self.context else None
        if user and user.is_authenticated:
            return obj.read_stats.filter(user=user).exists()
        return False


# 11. Serializer cho System Config (Branding)
class SystemConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = SystemConfig
        fields = [
            'brand_name', 'logo_url', 'navbar_color', 'brand_color',
            'link_color', 'link_hover_color', 'active_link_color',
            'active_link_bg_color', 'auto_save_enabled', 'updated_at'
        ]
        read_only_fields = ['updated_at']

