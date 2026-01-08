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
    Field, LoanProfile, Person, LoanProfilePerson, FieldValue, 
    DocumentTemplate, FieldGroup, Role, Asset, LoanProfileAsset, 
    FormView
)

# Import Serializers
from .serializers import (
    FieldSerializer, FieldGroupSerializer, LoanProfileSerializer, 
    PersonSerializer, FieldValueSerializer, DocumentTemplateSerializer,
    RoleSerializer, AssetSerializer, LoanProfilePersonSerializer,
    LoanProfileAssetSerializer, UserSerializer, FormViewSerializer, 
    MasterPersonSerializer, MasterAssetSerializer
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
            groups_qs = groups_qs.filter(entity_type=entity_type)
        elif form_slug:
            groups_qs = groups_qs.filter(allowed_forms__slug=form_slug).distinct()
            
        # 2. Prefetch fields
        fields_filter = Q(is_active=True)
        # Nếu là Master Data (có entity_type), ta lấy tất cả fields của group đó
        # Nếu là Hồ sơ (có form_slug), ta lọc fields được phép hiển thị ở form đó
        if not entity_type and form_slug:
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

# 2. ViewSet cho Person
class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    serializer_class = PersonSerializer
    permission_classes = [AllowAny]
    lookup_field = 'id'  # Ensure 'id' is used as the identifier


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
        updating_user = request.user if request.user.is_authenticated else None

        try:
            with transaction.atomic():
                # 1. Tạo hồ sơ mới
                new_profile = LoanProfile.objects.create(
                    name=new_name,
                    form_view=original.form_view,
                    created_by_user=request.user if request.user.is_authenticated else None
                )

                # 2. Sao chép FieldValues chung (không liên kết Person/Asset)
                general_fvs = original.fieldvalue_set.filter(person__isnull=True, asset__isnull=True)
                for fv in general_fvs:
                    FieldValue.objects.create(
                        loan_profile=new_profile,
                        field=fv.field,
                        person=None,
                        asset=None,
                        value=fv.value
                    )

                # 3. Sao chép People
                for link in original.linked_people.all():
                    old_person = link.person
                    # Tạo Person mới (vì Person chỉ là ID holder)
                    new_person = Person.objects.create(last_updated_by=updating_user)
                    
                    # Liên kết vào hồ sơ mới với vai trò
                    LoanProfilePerson.objects.create(
                        loan_profile=new_profile,
                        person=new_person,
                        roles=link.roles
                    )
                    
                    # Sao chép FieldValues của Person
                    person_fvs = original.fieldvalue_set.filter(person=old_person)
                    for fv in person_fvs:
                        FieldValue.objects.create(
                            loan_profile=new_profile,
                            field=fv.field,
                            person=new_person,
                            asset=None,
                            value=fv.value
                        )

                # 4. Sao chép Assets
                for link in original.linked_assets.all():
                    old_asset = link.asset
                    new_asset = Asset.objects.create(last_updated_by=updating_user)
                    
                    LoanProfileAsset.objects.create(
                        loan_profile=new_profile,
                        asset=new_asset
                    )
                    
                    # Sao chép FieldValues của Asset
                    asset_fvs = original.fieldvalue_set.filter(asset=old_asset)
                    for fv in asset_fvs:
                        FieldValue.objects.create(
                            loan_profile=new_profile,
                            field=fv.field,
                            person=None,
                            asset=new_asset,
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
        API lưu dữ liệu tổng hợp:
        - Cập nhật tên hồ sơ
        - Lưu FieldValues chung
        - Lưu/Cập nhật People và Roles
        - Lưu FieldValues riêng của từng người
        """
        loan_profile = self.get_object()
        data = request.data

        try:
            with transaction.atomic():
                # Xử lý Người dùng thực hiện (Audit)
                updating_user = request.user if request.user.is_authenticated else None

                # A. Cập nhật thông tin cơ bản
                if 'name' in data:
                    loan_profile.name = data['name']
                
                # Lưu form_view nếu có form_slug truyền vào
                form_slug = data.get('form_slug')
                if form_slug:
                    form_v = FormView.objects.filter(slug=form_slug).first()
                    if form_v:
                        loan_profile.form_view = form_v
                
                loan_profile.save()

                # B. Lưu FieldValues CHUNG
                general_fields = data.get('field_values', {})
                for key, val in general_fields.items():
                    try:
                        field_obj = Field.objects.get(placeholder_key=key)
                        FieldValue.objects.update_or_create(
                            loan_profile=loan_profile,
                            field=field_obj,
                            person=None,
                            asset=None,  # Không phải FieldValue của Asset
                            defaults={'value': str(val)}
                        )
                    except Field.DoesNotExist:
                        continue

                # C. Xử lý PEOPLE
                people_data = data.get('people', [])
                current_person_ids = []

                for p_data in people_data:
                    p_individual_fields = p_data.get('individual_field_values', {})
                    p_roles = p_data.get('roles', [])

                    # Lấy thông tin Name/CCCD từ fields động
                    # Fallback vào p_data['ho_ten'] nếu không có trong p_individual_fields (đề phòng)
                    p_name = p_individual_fields.get('ho_ten') or p_data.get('ho_ten', '')
                    p_cccd = p_individual_fields.get('cccd_so') or p_data.get('cccd_so', '')

                    if not p_name: continue
                    
                    # Tìm hoặc Tạo Person (Ưu tiên tìm theo CCCD)
                    person = None
                    if p_cccd:
                        # [REFACTOR] Tìm Person thông qua FieldValue 'cccd_so' thay vì column
                        # Tìm xem có bất kỳ Person nào đã từng có CCCD này trong hệ thống chưa (ở các hồ sơ khác)
                        existing_fv = FieldValue.objects.filter(
                            field__placeholder_key='cccd_so', 
                            value=p_cccd,
                            person__isnull=False
                        ).first()
                        
                        if existing_fv:
                            person = existing_fv.person
                            # Cập nhật thông tin truy vết - Audit
                            person.last_updated_by = updating_user
                            person.save()
                        else:
                            # Nếu không thấy, tạo mới (Person giờ chỉ là ID holder)
                            person = Person.objects.create(last_updated_by=updating_user)
                    else:
                        # Nếu không có CCCD, tạo mới luôn
                        person = Person.objects.create(last_updated_by=updating_user)

                    current_person_ids.append(person.id)  # Ensure Person model has id attribute

                    # Liên kết Person vào Profile
                    LoanProfilePerson.objects.update_or_create(
                        loan_profile=loan_profile,
                        person=person,
                        defaults={'roles': p_roles}
                    )

                    # Lưu FieldValues RIÊNG của Person
                    for key, val in p_individual_fields.items():
                        try:
                            field_obj = Field.objects.get(placeholder_key=key)
                            FieldValue.objects.update_or_create(
                                loan_profile=loan_profile,
                                field=field_obj,
                                person=person,
                                asset=None,  # Person FieldValue không thuộc Asset nào
                                defaults={'value': str(val)}
                            )
                        except Field.DoesNotExist:
                            continue

                # D. Dọn dẹp People (Xóa những người bị remove khỏi form)
                LoanProfilePerson.objects.filter(loan_profile=loan_profile).exclude(
                    person__id__in=current_person_ids).delete()
                FieldValue.objects.filter(loan_profile=loan_profile, person__isnull=False).exclude(
                    person__id__in=current_person_ids).delete()

                # E. Xử lý ASSETS (MỚI)
                assets_data = data.get('assets', [])
                current_asset_ids = []

                for a_data in assets_data:
                    a_field_values = a_data.get('asset_field_values', {})
                    a_id = a_data.get('id')
                    
                    # Tìm hoặc Tạo Asset
                    # Asset chỉ là ID holder, không có thuộc tính riêng (như name/cccd)
                    if a_id:
                        try:
                            asset = Asset.objects.get(id=a_id)
                            asset.last_updated_by = updating_user
                            asset.save()
                        except Asset.DoesNotExist:
                            # Nếu ID không tồn tại (hiếm khi xảy ra do UI), tạo mới
                            asset = Asset.objects.create(last_updated_by=updating_user)
                    else:
                         asset = Asset.objects.create(last_updated_by=updating_user)
                    
                    current_asset_ids.append(asset.id)

                    # Liên kết Asset vào Profile
                    LoanProfileAsset.objects.get_or_create(
                        loan_profile=loan_profile,
                        asset=asset
                    )

                    # Lưu FieldValues RIÊNG của Asset
                    for key, val in a_field_values.items():
                        try:
                            field_obj = Field.objects.get(placeholder_key=key)
                            FieldValue.objects.update_or_create(
                                loan_profile=loan_profile,
                                field=field_obj,
                                person=None,  # Asset FieldValue không thuộc Person nào
                                asset=asset,
                                defaults={'value': str(val)}
                            )
                        except Field.DoesNotExist:
                            continue

                # F. Dọn dẹp Assets
                LoanProfileAsset.objects.filter(loan_profile=loan_profile).exclude(
                    asset__id__in=current_asset_ids).delete()
                FieldValue.objects.filter(loan_profile=loan_profile, asset__isnull=False).exclude(
                    asset__id__in=current_asset_ids).delete()

            return Response({"status": "success", "message": "Lưu dữ liệu thành công!"}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        # Tối ưu hóa truy vấn: Lấy luôn dữ liệu bảng con trong 1 lần
        queryset = LoanProfile.objects.all().prefetch_related(
            'fieldvalue_set__field',  # Load sẵn FieldValue và thông tin Field
            'linked_people__person'  # Load sẵn bảng liên kết và thông tin Person
        )
        # ... logic lọc theo user (nếu có) ...
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

        # C. Danh sách Người (People List)
        people_list = []
        # Lấy qua bảng trung gian LoanProfilePerson (related_name='linked_people')
        links = loan_profile.linked_people.select_related('person').all()

        for link in links:
            person = link.person
            # Lấy các trường riêng của người này trong hồ sơ này (Địa chỉ, SĐT...)
            person_fvs = loan_profile.fieldvalue_set.filter(person=person)
            
            # Helper để lấy giá trị từ queryset
            def get_val(key):
                fv = next((x for x in person_fvs if x.field.placeholder_key == key), None)
                return fv.value if fv else ""

            p_data = {
                'ho_ten': get_val('ho_ten'),
                'cccd_so': get_val('cccd_so') or get_val('cccd'),  # Linh hoạt cả 2 key
                'cccd': get_val('cccd') or get_val('cccd_so'),     # Linh hoạt cả 2 key
                'roles': link.roles,  # Mảng các vai trò
            }
            for fv in person_fvs:
                p_data[fv.field.placeholder_key] = fv.value

            people_list.append(p_data)

        context['people'] = people_list

        # D. Danh sách Tài sản (Assets List)
        assets_list = []
        asset_links = loan_profile.linked_assets.select_related('asset').all()

        for link in asset_links:
            asset = link.asset
            asset_fvs = loan_profile.fieldvalue_set.filter(asset=asset)
            
            a_data = {
                'id': asset.id
            }
            for fv in asset_fvs:
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

# 10. ViewSets phục vụ Master Data (Quản lý tập trung)
def save_master_field_values(instance, field_values, entity_type_obj='person'):
    """Helper để lưu dynamic field values cho Master Data (loan_profile=None)"""
    if not field_values:
        return
    
    for key, val in field_values.items():
        try:
            field_obj = Field.objects.get(placeholder_key=key)
            # Chỉ lưu nếu field này thuộc về đúng entity type (tránh lưu rác)
            if field_obj.group and field_obj.group.entity_type.lower() != entity_type_obj.lower():
                # Đặc biệt: Nếu là person, chấp nhận cả 'PERSON'
                # Nếu là asset, chấp nhận cả 'ASSET'
                pass

            params = {
                'loan_profile': None,
                'field': field_obj,
                'defaults': {'value': str(val)}
            }
            if entity_type_obj == 'person':
                params['person'] = instance
                params['asset'] = None
            else:
                params['asset'] = instance
                params['person'] = None
            
            FieldValue.objects.update_or_create(**params)
        except Field.DoesNotExist:
            continue

class MasterPersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all().order_by('-id')
    serializer_class = MasterPersonSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        updating_user = self.request.user if not self.request.user.is_anonymous else None
        instance = serializer.save(last_updated_by=updating_user)
        field_values = self.request.data.get('field_values', {})
        save_master_field_values(instance, field_values, 'person')

    def perform_update(self, serializer):
        updating_user = self.request.user if not self.request.user.is_anonymous else None
        instance = serializer.save(last_updated_by=updating_user)
        field_values = self.request.data.get('field_values', {})
        save_master_field_values(instance, field_values, 'person')

    @action(detail=True, methods=['get'])
    def related_profiles(self, request, pk=None):
        person = self.get_object()
        links = LoanProfilePerson.objects.filter(person=person).select_related('loan_profile')
        profiles = [link.loan_profile for link in links]
        data = []
        for p in profiles:
            data.append({
                'id': p.id,
                'name': p.name,
                'created_at': p.created_at,
                'form_name': p.form_view.name if p.form_view else 'Mặc định'
            })
        return Response(data)

    @action(detail=True, methods=['get'])
    def related_assets(self, request, pk=None):
        person = self.get_object()
        profile_ids = LoanProfilePerson.objects.filter(person=person).values_list('loan_profile_id', flat=True)
        asset_links = LoanProfileAsset.objects.filter(loan_profile_id__in=profile_ids).select_related('asset')
        assets = set([link.asset for link in asset_links])
        
        data = []
        for a in assets:
            fv = FieldValue.objects.filter(asset=a, field__placeholder_key='so_giay_chung_nhan').first()
            data.append({
                'id': a.id,
                'so_giay_chung_nhan': fv.value if fv else 'N/A',
                'created_at': a.created_at
            })
        return Response(data)

class MasterAssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.all().order_by('-id')
    serializer_class = MasterAssetSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        updating_user = self.request.user if not self.request.user.is_anonymous else None
        instance = serializer.save(last_updated_by=updating_user)
        field_values = self.request.data.get('field_values', {})
        save_master_field_values(instance, field_values, 'asset')

    def perform_update(self, serializer):
        updating_user = self.request.user if not self.request.user.is_anonymous else None
        instance = serializer.save(last_updated_by=updating_user)
        field_values = self.request.data.get('field_values', {})
        save_master_field_values(instance, field_values, 'asset')

    @action(detail=True, methods=['get'])
    def related_profiles(self, request, pk=None):
        asset = self.get_object()
        links = LoanProfileAsset.objects.filter(asset=asset).select_related('loan_profile')
        profiles = [link.loan_profile for link in links]
        data = []
        for p in profiles:
            data.append({
                'id': p.id,
                'name': p.name,
                'created_at': p.created_at,
                'form_name': p.form_view.name if p.form_view else 'Mặc định'
            })
        return Response(data)
