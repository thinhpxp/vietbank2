from rest_framework import viewsets, status
from django.contrib.auth.models import User
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.db import transaction
from django.db.models import Prefetch
# --- CÁC IMPORT MỚI CHO CHỨC NĂNG XUẤT WORD ---
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from docxtpl import DocxTemplate
from datetime import datetime
import os
import io
from num2words import num2words # Cần pip install num2words
import decimal
from jinja2 import Environment
# Import Models
from .models import (
    Field, LoanProfile, FieldValue, 
    DocumentTemplate, FieldGroup, Role, 
    FormView, MasterObject, LoanProfileObjectLink,
    MasterObjectType, MasterObjectRelation # ADDED
)

# Import Serializers
from .serializers import (
    FieldSerializer, FieldGroupSerializer, LoanProfileSerializer, 
    FieldValueSerializer, DocumentTemplateSerializer,
    RoleSerializer,
    UserSerializer, FormViewSerializer, MasterObjectSerializer, 
    LoanProfileObjectLinkSerializer, MasterObjectTypeSerializer,
    MasterObjectRelationSerializer # ADDED
)
# --- CÁC HÀM HỖ TRỢ JINJA2 (FORMAT TIỀN, NGÀY, CHỮ) ---
def format_currency_filter(value):
    """Chuyển số thành dạng tiền tệ (VD: 1.000.000)"""
    if not value: return ""
    try:
        d_value = decimal.Decimal(str(value))
        return "{:,.0f}".format(d_value).replace(",", ".")
    except:
        return str(value)

def num2words_filter(value):
    """Chuyển số thành chữ Tiếng Việt (có hỗ trợ số thập phân)"""
    if not value: return ""
    try:
        import re
        # Chuẩn hóa: phẩy -> chấm, xóa khoảng trắng
        s_val = str(value).replace(',', '.').replace(' ', '')
        # Loại bỏ các dấu chấm phân tách hàng nghìn (dots that are not the decimal point)
        # Tuy nhiên, cách an toàn nhất là chỉ giữ lại dấu chấm cuối cùng nếu có nhiều hơn 1 dot
        # Hoặc đơn giản hơn: Theo logic mới của Frontend, state chỉ có duy nhất 1 dấu chấm cho decimal.
        # Vậy ta chỉ cần strip mọi dấu chấm trừ cái cuối cùng? Không, strip mọi dấu chấm trừ cái duy nhất.
        
        # Logic: Tìm dot cuối cùng. Xóa tất cả dot khác.
        parts = s_val.split('.')
        if len(parts) > 2:
            # Có nhiều hơn 1 dot -> Có dấu phân tách nghìn lọt vào
            clean_val = "".join(parts[:-1]) + "." + parts[-1]
        else:
            clean_val = s_val
            
        # Chỉ giữ lại số và dấu chấm
        clean_val = re.sub(r'[^\d.]', '', clean_val)
        
        if not clean_val: return str(value)
        
        # Đọc số (Dùng float nếu có dấu chấm)
        if '.' in clean_val:
            val_to_read = float(clean_val)
        else:
            val_to_read = int(clean_val)
            
        result = num2words(val_to_read, lang='vi').capitalize()
        return result
    except Exception as e:
        print(f"DEBUG: num2words_filter failed for value '{value}': {e}")
        return str(value)

def to_roman_filter(value):
    """Chuyển số thành ký tự La Mã viết thường (i, ii, iii...)"""
    try:
        n = int(value)
        if not 0 < n < 4000: return str(value)
        millions = ["", "m", "mm", "mmm"]
        hundreds = ["", "c", "cd", "d", "dc", "dcc", "dccc", "cm"]
        tens = ["", "x", "xx", "xxx", "xl", "l", "lx", "lxx", "lxxx", "xc"]
        ones = ["", "i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix"]
        return millions[n // 1000] + hundreds[(n % 1000) // 100] + tens[(n % 100) // 10] + ones[n % 10]
    except:
        return str(value)

def dateformat_filter(value, fmt="%d/%m/%Y"):
    """
    Định dạng ngày tháng thông minh. 
    Hỗ trợ cả object datetime và chuỗi văn bản (kể cả chuỗi thiếu thông tin).
    Nếu thành phần nào thiếu (ví dụ ngày trống), sẽ tự động điền dấu chấm vào vị trí đó.
    """
    import re
    empty_dots = " . . . . "
    
    if not value: 
        return " . . . . . . . . " if fmt == "%d/%m/%Y" else empty_dots
        
    # 1. Thử parse thành object datetime nếu là chuỗi chuẩn
    dt = None
    if isinstance(value, datetime):
        dt = value
    elif isinstance(value, str):
        for str_fmt in ['%Y-%m-%d', '%d/%m/%Y', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d %H:%M:%S']:
            try:
                dt = datetime.strptime(value.strip(), str_fmt)
                break
            except:
                continue
                
    if dt:
        return dt.strftime(fmt)
        
    # 2. Xử lý chuỗi "văn bản tự do" (ví dụ: " /12/2025")
    if isinstance(value, str):
        # Tách chuỗi bằng các ký tự phân cách phổ biến
        parts = re.split(r'[/.\-]', value.strip())
        
        # Dự đoán vị trí Ngày, Tháng, Năm
        day = month = year = None
        
        if len(parts) == 3:
            # Giả định định dạng DD/MM/YYYY hoặc YYYY-MM-DD
            if len(parts[0]) == 4: # YYYY-MM-DD
                year, month, day = parts
            else: # DD/MM/YYYY
                day, month, year = parts
        elif len(parts) == 2: # MM/YYYY
            month, year = parts
            
        # Hàm kiểm tra xem một phần có "hợp lệ" hay không
        def clean_part(v):
            if not v or not re.search(r'\d', str(v)):
                return empty_dots
            return str(v).strip()
            
        # Thay thế các token trong định dạng bằng giá trị tương ứng
        res = fmt
        res = res.replace('%d', clean_part(day))
        res = res.replace('%m', clean_part(month))
        res = res.replace('%Y', clean_part(year))
        # Hỗ trợ năm rút gọn %y
        y_val = clean_part(year)
        res = res.replace('%y', y_val[-2:] if len(y_val) >= 2 and y_val != empty_dots else empty_dots)
        
        return res
        
    return str(value) if value else " . . . . . . . . "
# -----------------------------------------------------
# 1.1 ViewSet cho FieldGroup (MỚI)
class FieldGroupViewSet(viewsets.ModelViewSet):
    queryset = FieldGroup.objects.all().order_by('order')
    serializer_class = FieldGroupSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset()
        form_slug = self.request.query_params.get('form_slug')
        if form_slug is not None:
            # Chết độ lọc nghiêm ngặt: Chỉ lấy những nhóm được gắn trực tiếp với form này
            queryset = queryset.filter(allowed_forms__slug=form_slug).distinct()
        return queryset

# 1.1b ViewSet cho FormView (MỚI)
class FormViewViewSet(viewsets.ModelViewSet):
    queryset = FormView.objects.all()
    serializer_class = FormViewSerializer
    permission_classes = [AllowAny]

# 1.3 ViewSet cho Role
class RoleViewSet(viewsets.ModelViewSet):
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [AllowAny]

# 1.2 ViewSet cho Field
class FieldViewSet(viewsets.ModelViewSet):
    queryset = Field.objects.all()
    serializer_class = FieldSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        queryset = super().get_queryset().select_related('group')
        form_slug = self.request.query_params.get('form_slug')
        if form_slug is not None:
            # Chết độ cực kỳ nghiêm ngặt: Phải được gán đích danh Form này 
            # VÀ Nhóm của nó cũng phải được gán cho Form này
            queryset = queryset.filter(
                allowed_forms__slug=form_slug,
                group__allowed_forms__slug=form_slug
            ).distinct()
        return queryset

    def destroy(self, request, *args, **kwargs):
        """Ngăn xóa các trường được bảo vệ"""
        instance = self.get_object()
        if instance.is_protected:
            return Response(
                {"error": "Không thể xóa trường được bảo vệ."},
                status=status.HTTP_400_BAD_REQUEST
            )
        return super().destroy(request, *args, **kwargs)



    @action(detail=False, methods=['get'])
    def active_fields_grouped(self, request):
        """Trả về danh sách trường active nhóm theo FieldGroup, có lọc theo form_slug hoặc entity_type"""
        form_slug = request.query_params.get('form_slug')
        entity_type = request.query_params.get('entity_type') # MỚI: Lọc theo đối tượng (PERSON, ASSET, ...)
        
        from django.db.models import Q
        
        # 1. Lọc nhóm
        groups_qs = FieldGroup.objects.all().order_by('order')
        if entity_type:
            # Hỗ trợ cả cơ chế cũ (entity_type) và mới (object_type__code)
            groups_qs = groups_qs.filter(
                Q(object_type__code=entity_type) | 
                Q(entity_type=entity_type)
            ).distinct()
        elif form_slug:
            groups_qs = groups_qs.filter(allowed_forms__slug=form_slug).distinct()
            
        # 2. Prefetch fields
        fields_filter = Q(is_active=True)
        
        # NEW: If entity_type is provided, filter fields by allowed_object_types containing this type
        if entity_type:
            fields_filter &= Q(allowed_object_types__code=entity_type)
        elif form_slug:
            # Nếu là Hồ sơ (có form_slug), ta lọc fields được phép hiển thị ở form đó
            fields_filter &= Q(allowed_forms__slug=form_slug)
            
        groups = groups_qs.prefetch_related(
            Prefetch('fields', queryset=Field.objects.filter(fields_filter).distinct())
        )

        result = {}
        for grp in groups:
            fields_data = FieldSerializer(grp.fields.all(), many=True).data
            if fields_data:
                result[grp.name] = fields_data

        # Synthetic fields: Chỉ hiện ở bản cũ hoặc khi không có entity_type
        if not entity_type:
            result["Thông tin cá nhân"] = [] 

        return Response(result)

# PersonViewSet removed


# 3.1 ViewSet cho DocumentTemplate
class DocumentTemplateViewSet(viewsets.ModelViewSet):
    # Upload dành cho Admin trang quản trị
    queryset = DocumentTemplate.objects.all()
    serializer_class = DocumentTemplateSerializer
    permission_classes = [AllowAny] # Hoặc IsAuthenticated

# 3.2 ViewSet cho User (MỚI)
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny] # Nên là IsAdminUser

# 4. ViewSet cho LoanProfile (Logic chính)
class LoanProfileViewSet(viewsets.ModelViewSet):
    queryset = LoanProfile.objects.all()
    serializer_class = LoanProfileSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        # Tự động gán user tạo nếu đã đăng nhập
        if self.request.user.is_authenticated:
            serializer.save(created_by_user=self.request.user)
        else:
            serializer.save()

    @action(detail=True, methods=['post'])
    def duplicate(self, request, pk=None):
        """
        API tạo bản sao hồ sơ vay.
        Input: { "new_name": "Tên hồ sơ mới" }
        Output: { "id": new_profile_id, "name": "..." }
        """
        original = self.get_object()
        new_name = request.data.get('new_name', f"Bản sao - {original.name}")
        
        try:
            with transaction.atomic():
                # 1. Tạo hồ sơ mới
                new_profile = LoanProfile.objects.create(
                    name=new_name,
                    form_view=original.form_view,
                    created_by_user=request.user if request.user.is_authenticated else None
                )

                # 2. Sao chép FieldValues chung (không liên kết Object)
                general_fvs = original.fieldvalue_set.filter(master_object__isnull=True)
                for fv in general_fvs:
                    FieldValue.objects.create(
                        loan_profile=new_profile,
                        field=fv.field,
                        value=fv.value
                    )

                # 3. Sao chép Objects (People/Assets/etc)
                for link in original.object_links.all():
                    master_obj = link.master_object
                    # Duplicate link
                    LoanProfileObjectLink.objects.create(
                        loan_profile=new_profile,
                        master_object=master_obj,
                        roles=link.roles
                    )
                    
                    # Duplicate specific FieldValues
                    specific_fvs = original.fieldvalue_set.filter(master_object=master_obj)
                    for fv in specific_fvs:
                        FieldValue.objects.create(
                            loan_profile=new_profile,
                            master_object=master_obj,
                            field=fv.field,
                            value=fv.value
                        )

            return Response({
                "status": "success",
                "id": new_profile.id,
                "name": new_profile.name,
                "message": "Tạo bản sao thành công!"
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                "status": "error",
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def save_form_data(self, request, pk=None):
        """
        API lưu dữ liệu tổng hợp (Generic for Universal Entity)
        """
        loan_profile = self.get_object()
        data = request.data
        updating_user = request.user if request.user.is_authenticated else None

        try:
            with transaction.atomic():
                # A. Cập nhật thông tin cơ bản
                if 'name' in data:
                    loan_profile.name = data['name']
                
                form_slug = data.get('form_slug')
                if form_slug:
                    form_v = FormView.objects.filter(slug=form_slug).first()
                    if form_v:
                        loan_profile.form_view = form_v
                
                loan_profile.save()

                # B. Lưu FieldValues chung
                general_fields = data.get('field_values', {})
                for key, val in general_fields.items():
                    try:
                        field_obj = Field.objects.get(placeholder_key=key)
                        FieldValue.objects.update_or_create(
                            loan_profile=loan_profile,
                            master_object=None,
                            field=field_obj,
                            defaults={'value': str(val)}
                        )
                    except Field.DoesNotExist:
                        continue

                # C. Xử lý Objects (Unified Logic for People and Assets)
                processed_master_ids = []

                def process_objects(data_list, default_obj_type):
                    for item_data in data_list:
                        obj_id = item_data.get('id')
                        roles = item_data.get('roles', [])
                        fields_dict = item_data.get('individual_field_values') or item_data.get('asset_field_values', {})
                        
                        # Extract actual type from payload if present (NEW)
                        actual_type = default_obj_type
                        if 'master_object' in item_data and item_data['master_object']:
                            actual_type = item_data['master_object'].get('object_type', default_obj_type)
                        
                        # 1. Find or Create MasterObject
                        master_obj = None
                        if obj_id:
                            master_obj = MasterObject.objects.filter(id=obj_id).first()
                            if master_obj:
                                master_obj.last_updated_by = updating_user
                                master_obj.save()
                        
                        # DEDUPLICATION LOGIC: Nếu chưa có id, thử tìm theo mã định danh (CCCD, Biển số...)
                        if not master_obj:
                            master_obj = find_existing_master_object(actual_type, fields_dict)
                        
                        if not master_obj:
                            master_obj = MasterObject.objects.create(
                                object_type=actual_type,
                                last_updated_by=updating_user
                            )

                        processed_master_ids.append(master_obj.id)

                        # 2. Update Link
                        LoanProfileObjectLink.objects.update_or_create(
                            loan_profile=loan_profile,
                            master_object=master_obj,
                            defaults={'roles': roles}
                        )

                        # 3. Save Specific Field Values
                        for f_key, f_val in fields_dict.items():
                            try:
                                f_obj = Field.objects.get(placeholder_key=f_key)
                                FieldValue.objects.update_or_create(
                                    loan_profile=loan_profile,
                                    master_object=master_obj,
                                    field=f_obj,
                                    defaults={'value': str(f_val)}
                                )

                                # 4. Update Canonical Master Data (loan_profile=None)
                                # This ensures the object appears correctly in Master Data Management
                                FieldValue.objects.update_or_create(
                                    loan_profile=None,
                                    master_object=master_obj,
                                    field=f_obj,
                                    defaults={'value': str(f_val)}
                                )
                            except Field.DoesNotExist:
                                continue

                process_objects(data.get('people', []), 'PERSON')
                process_objects(data.get('assets', []), 'ASSET')

                # D. Cleanup
                LoanProfileObjectLink.objects.filter(loan_profile=loan_profile).exclude(
                    master_object__id__in=processed_master_ids
                ).delete()
                
                # E. AUTOMATIC RELATION INFERENCE (Direct Linking)
                # Logic: If a Person has a Role with relation_type (e.g., OWNER), link them to all Assets in this profile.
                # 1. Find potential owners in this profile
                potential_owners = []
                # Re-fetch links to get fresh roles
                profile_links = LoanProfileObjectLink.objects.filter(loan_profile=loan_profile).select_related('master_object')
                
                for link in profile_links:
                    if link.master_object.object_type == 'PERSON':
                        # Check roles
                        if not link.roles: continue
                        
                        # Find if any role implies a relation
                        # We need to query Role table or cache it. Since roles are list of strings (slugs), we match with Role.slug
                        # Optimization: Fetch all system roles with relation_type once
                        system_roles = Role.objects.exclude(relation_type__isnull=True).exclude(relation_type='')
                        
                        for role_str in link.roles:
                            # Match slug OR name (case insensitive safe if needed, but strict for now)
                            matching_role = next((r for r in system_roles if r.slug == role_str or r.name == role_str), None)
                            if matching_role:
                                potential_owners.append({
                                    'person': link.master_object,
                                    'relation': matching_role.relation_type
                                })

                # 2. Find assets in this profile
                assets_in_profile = [link.master_object for link in profile_links if link.master_object.object_type != 'PERSON']
                
                # 3. Create Relations
                if potential_owners and assets_in_profile:
                    for owner_data in potential_owners:
                        person = owner_data['person']
                        rtype = owner_data['relation']
                        
                        for asset in assets_in_profile:
                            # Create or Get Relation
                            MasterObjectRelation.objects.get_or_create(
                                source_object=person,
                                target_object=asset,
                                relation_type=rtype
                            )
                
                FieldValue.objects.filter(loan_profile=loan_profile, master_object__isnull=False).exclude(
                    master_object__id__in=processed_master_ids
                ).delete()

            return Response({"status": "success", "message": "Lưu dữ liệu thành công!"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        # Tối ưu hóa truy vấn: Lấy luôn dữ liệu bảng con trong 1 lần
        queryset = LoanProfile.objects.all().prefetch_related(
            'fieldvalue_set__field',
            'object_links__master_object'
        )
        return queryset

    @action(detail=True, methods=['post'], url_path='generate-document')
    def generate_document(self, request, pk=None):
        """
        API sinh file Word từ Template và Dữ liệu hồ sơ.
        Input: { "template_id": 1 }
        Output: File .docx
        """
        loan_profile = self.get_object()
        template_id = request.data.get('template_id')

        if not template_id:
            return Response({"error": "Vui lòng cung cấp template_id."}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Lấy file mẫu
        document_template = get_object_or_404(DocumentTemplate, id=template_id)
        template_path = document_template.file.path

        if not os.path.exists(template_path):
            return Response({"error": "File mẫu không tồn tại trên server."}, status=status.HTTP_404_NOT_FOUND)

        # 2. CHUẨN BỊ CONTEXT (Dữ liệu để trộn)
        context = {}

        # A. Thông tin cơ bản
        context['ten_ho_so'] = loan_profile.name
        
        # Xử lý Ngày lập hồ sơ (ngay_tao) ưu tiên lấy từ trường động 'ngay_lap_ho_so'
        ngay_lap_fv = loan_profile.fieldvalue_set.filter(
            field__placeholder_key='ngay_lap_ho_so', 
            person__isnull=True, 
            asset__isnull=True
        ).first()
        
        if ngay_lap_fv:
            # Nếu có dữ liệu (bao gồm cả chuỗi rỗng nếu người dùng muốn để trắng)
            context['ngay_tao'] = ngay_lap_fv.value if ngay_lap_fv.value else ""
        else:
            # Fallback cho các hồ sơ cũ chưa có trường này
            context['ngay_tao'] = loan_profile.created_at

        # B. Các trường chung (FieldValues không gắn với Person hoặc Asset)
        # Biến đổi từ: {field: "so_tien", value: "100"} -> context["so_tien"] = "100"
        general_fvs = loan_profile.fieldvalue_set.filter(person__isnull=True, asset__isnull=True)
        for fv in general_fvs:
            context[fv.field.placeholder_key] = fv.value

        # C. Danh sách People (from Universal)
        people_list = []
        person_links = loan_profile.object_links.filter(master_object__object_type='PERSON').select_related('master_object')

        for link in person_links:
            master = link.master_object
            specific_fvs = loan_profile.fieldvalue_set.filter(master_object=master)
            
            def get_val(key):
                fv = next((x for x in specific_fvs if x.field.placeholder_key == key), None)
                if fv: return fv.value
                # Master fallback
                master_fv = FieldValue.objects.filter(master_object=master, field__placeholder_key=key, loan_profile__isnull=True).first()
                return master_fv.value if master_fv else ""

            p_data = {
                'ho_ten': get_val('ho_ten'),
                'cccd_so': get_val('cccd_so'),
                'roles': link.roles,
            }
            # Add all known values
            for fv in specific_fvs:
                p_data[fv.field.placeholder_key] = fv.value
            
            people_list.append(p_data)

        context['people'] = people_list

        # D. Danh sách Assets (from Universal)
        assets_list = []
        asset_links = loan_profile.object_links.filter(master_object__object_type='ASSET').select_related('master_object')

        for link in asset_links:
            master = link.master_object
            specific_fvs = loan_profile.fieldvalue_set.filter(master_object=master)
            
            a_data = {'id': master.id}
            for fv in specific_fvs:
                a_data[fv.field.placeholder_key] = fv.value
                
            assets_list.append(a_data)
        
        context['assets'] = assets_list

        # E. Tạo các danh sách lọc sẵn dựa trên VAI TRÒ (Gộp cả Slug động và Legacy)
        # 1. Lấy danh sách Role từ DB để làm bản đồ Mapping
        all_system_roles = Role.objects.exclude(slug__isnull=True).exclude(slug='')
        
        # Bản đồ: tên_vai_trò (lowercase) -> slug (lowercase)
        role_name_to_slug = {}
        all_active_slugs = set()
        for r in all_system_roles:
            s = r.slug.strip().lower()
            role_name_to_slug[r.name.strip().lower()] = s
            all_active_slugs.add(s)

        # 2. Định nghĩa các Slug mặc định (Legacy)
        legacy_slug_map = {
            'ben_vay': ['bên vay', 'bên được cấp tín dụng'],
            'ben_duoc_cap_tin_dung': ['bên được cấp tín dụng'],
            'ben_the_chap': ['bên thế chấp', 'bên bảo đảm'],
            'ben_bao_dam': ['bên bảo đảm', 'bên thế chấp', 'bên bảo đảm'],
            'ben_bao_lanh': ['bên bảo lãnh']
        }
        for s in legacy_slug_map:
            all_active_slugs.add(s)

        # 3. Khởi tạo các danh sách trong context (tất cả là lowercase slug)
        role_data_lists = {s: [] for s in all_active_slugs}

        # 4. Phân loại từng người vào các danh sách phù hợp
        for p in people_list:
            p_assigned_roles = [r.strip().lower() for r in p.get('roles', [])]
            matched_slugs = set()
            
            for rname in p_assigned_roles:
                # a. Tìm theo Slug động trong DB
                if rname in role_name_to_slug:
                    matched_slugs.add(role_name_to_slug[rname])
                
                # b. Tìm theo logic Legacy (fallback)
                for l_slug, l_names in legacy_slug_map.items():
                    if rname in l_names:
                        matched_slugs.add(l_slug)
            
            # Đưa người này vào tất cả các danh sách đã khớp
            for s in matched_slugs:
                role_data_lists[s].append(p)
        
        # 5. Đưa vào context với hậu tố _list
        for s, plist in role_data_lists.items():
            context[f"{s}_list"] = plist
            
        # 6. Alias đặc biệt (Chống lỗi gõ thiếu dấu hoặc sai legacy key)
        if 'ben_vay_list' in context:
            context['tin_dung_list'] = context['ben_vay_list'] # Alias phổ biến
        if 'ben_bao_dam_list' in context:
            context['bao_dam_list'] = context['ben_bao_dam_list'] # Alias phổ biến

        # 3. XỬ LÝ TEMPLATE VÀ SINH FILE
        try:
            doc = DocxTemplate(template_path)

            # --- SỬA LỖI: CÁCH ĐĂNG KÝ FILTER CHUẨN ---
            # 1. Tạo một môi trường Jinja2 mới
            jinja_env = Environment()

            # 2. Đăng ký các hàm filter của chúng ta vào môi trường này
            jinja_env.filters['format_currency'] = format_currency_filter
            jinja_env.filters['num2words'] = num2words_filter
            jinja_env.filters['dateformat'] = dateformat_filter
            jinja_env.filters['to_roman'] = to_roman_filter

            # 3. Truyền môi trường (jinja_env) vào hàm render
            doc.render(context, jinja_env=jinja_env)
            # ------------------------------------------

            # Lưu vào bộ nhớ đệm (RAM) thay vì ghi ra đĩa cứng
            file_stream = io.BytesIO()
            doc.save(file_stream)
            file_stream.seek(0)  # Đưa con trỏ về đầu file

            # Tạo tên file output
            # Lưu ý: Xử lý tên file để tránh lỗi encoding khi download
            safe_filename = f"HopDong_{loan_profile.id}_{document_template.name}".encode('utf-8', 'ignore').decode(
                'utf-8')
            safe_filename = safe_filename.replace(" ", "_") + ".docx"

            # Trả về file cho trình duyệt tải xuống
            response = FileResponse(file_stream, as_attachment=True, filename=safe_filename)

            # Cấu hình header bổ sung để đảm bảo Frontend đọc được tên file
            response['Content-Disposition'] = f'attachment; filename="{safe_filename}"'
            response['Access-Control-Expose-Headers'] = 'Content-Disposition'

            return response

        except Exception as e:
            print(f"Lỗi sinh file: {e}")
            # In chi tiết lỗi ra console server để debug nếu cần
            import traceback
            traceback.print_exc()
            return Response({"error": f"Lỗi sinh file: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# 10. ViewSets phục vụ Master Data (Universal)
def save_master_field_values(instance, field_values):
    """Generic helper để lưu dynamic field values cho MasterObject"""
    if not field_values:
        return
    
    for key, val in field_values.items():
        try:
            field_obj = Field.objects.get(placeholder_key=key)
            # Không cần check entity type ở đây vì đã check ở frontend
            
            FieldValue.objects.update_or_create(
                master_object=instance,
                loan_profile=None,
                field=field_obj,
                defaults={'value': str(val)}
            )
        except Field.DoesNotExist:
            continue

def find_existing_master_object(object_type, field_values):
    """
    Tìm kiếm MasterObject đã tồn tại dựa trên identity_field_key của loại đối tượng đó.
    """
    if not object_type or not field_values:
        return None
        
    try:
        from .models import MasterObjectType, FieldValue
        obj_type_config = MasterObjectType.objects.filter(code=object_type).first()
        if not obj_type_config or not obj_type_config.identity_field_key:
            return None
            
        id_key = obj_type_config.identity_field_key
        id_value = field_values.get(id_key)
        
        if not id_value:
            return None
            
        # 2. Tìm kiếm FieldValue khớp với key và value (ở mức Master, loan_profile=None)
        matching_fv = FieldValue.objects.filter(
            master_object__object_type=object_type,
            field__placeholder_key=id_key,
            value=str(id_value),
            loan_profile__isnull=True
        ).first()
        
        return matching_fv.master_object if matching_fv else None
    except Exception as e:
        print(f"Error in find_existing_master_object: {e}")
        return None

    except Exception as e:
        print(f"Error in find_existing_master_object: {e}")
        return None

# --- RELATION VIEWSET ---
class MasterObjectRelationViewSet(viewsets.ModelViewSet):
    queryset = MasterObjectRelation.objects.all().order_by('-created_at')
    serializer_class = MasterObjectRelationSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'])
    def create_relation(self, request):
        """API thủ công để tạo quan hệ (dùng cho nút 'Gán quan hệ' ở Frontend)"""
        source_id = request.data.get('source_id')
        target_id = request.data.get('target_id')
        rtype = request.data.get('relation_type', 'OWNER')

        if not source_id or not target_id:
            return Response({"error": "Thiếu source_id hoặc target_id"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            source = MasterObject.objects.get(id=source_id)
            target = MasterObject.objects.get(id=target_id)
            
            relation, created = MasterObjectRelation.objects.get_or_create(
                source_object=source,
                target_object=target,
                relation_type=rtype
            )
            
            return Response(MasterObjectRelationSerializer(relation).data)
        except MasterObject.DoesNotExist:
            return Response({"error": "Không tìm thấy đối tượng"}, status=status.HTTP_404_NOT_FOUND)

# --- UNIVERSAL ENTITY VIEWSETS ---

class MasterObjectTypeViewSet(viewsets.ModelViewSet):
    queryset = MasterObjectType.objects.all().order_by('code')
    serializer_class = MasterObjectTypeSerializer
    permission_classes = [AllowAny] 
    # Trong thực tế nên hạn chế quyền sửa đổi cho Admin


class MasterObjectViewSet(viewsets.ModelViewSet):
    queryset = MasterObject.objects.all().order_by('-id')
    serializer_class = MasterObjectSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        """Filter by object_type (can be comma-separated) if provided in query params"""
        queryset = super().get_queryset()
        object_types = self.request.query_params.get('object_type', None)
        if object_types:
            codes = [c.strip() for c in object_types.split(',') if c.strip()]
            if codes:
                queryset = queryset.filter(object_type__in=codes)
        return queryset

    def perform_create(self, serializer):
        object_type = self.request.data.get('object_type')
        field_values = self.request.data.get('field_values', {})
        
        # Kiểm tra trùng lặp trước khi tạo
        existing = find_existing_master_object(object_type, field_values)
        if existing:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"message": f"Dữ liệu này đã tồn tại trong hệ thống (ID: {existing.id})", "code": "duplicate"})

        user = self.request.user if not self.request.user.is_anonymous else None
        instance = serializer.save(last_updated_by=user)
        save_master_field_values(instance, field_values)

    def perform_update(self, serializer):
        user = self.request.user if not self.request.user.is_anonymous else None
        instance = serializer.save(last_updated_by=user)
        field_values = self.request.data.get('field_values', {})
        save_master_field_values(instance, field_values)

    @action(detail=False, methods=['get'])
    def check_identity(self, request):
        """
        Kiểm tra nhanh xem một mã định danh đã tồn tại chưa.
        Params: object_type, key, value
        """
        obj_type = request.query_params.get('object_type')
        key = request.query_params.get('key')
        value = request.query_params.get('value')
        
        if not all([obj_type, key, value]):
            return Response({"error": "Missing params"}, status=400)
            
        existing = find_existing_master_object(obj_type, {key: value})
        if existing:
            return Response({
                "exists": True,
                "id": existing.id,
                "display_name": existing.get_display_name(existing) # Note: the serializer method is accessible via instance but better use a helper or re-implement
            })
        
        return Response({"exists": False})

    @action(detail=True, methods=['get'])
    def related_profiles(self, request, pk=None):
        master_obj = self.get_object()
        # Find all profiles linked to this object
        links = LoanProfileObjectLink.objects.filter(master_object=master_obj).select_related('loan_profile')
        profiles = [link.loan_profile for link in links]
        
        data = []
        for p in profiles:
            form_name = p.form_view.name if p.form_view else 'Mặc định'
            data.append({
                'id': p.id,
                'name': p.name,
                'created_at': p.created_at,
                'form_name': form_name
            })
        return Response(data)
