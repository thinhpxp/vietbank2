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
from .models import Field, LoanProfile, Person, LoanProfilePerson, FieldValue, DocumentTemplate, FieldGroup, Role

# Import Serializers
from .serializers import (
    FieldSerializer,
    LoanProfileSerializer,
    PersonSerializer,
    DocumentTemplateSerializer,
    FieldGroupSerializer,
    DocumentTemplateSerializer,
    FieldGroupSerializer,
    UserSerializer,
    RoleSerializer
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
    """Chuyển số thành chữ Tiếng Việt"""
    if not value: return ""
    try:
        # Xóa dấu chấm/phẩy nếu là string định dạng tiền
        clean_val = str(value).replace('.', '').replace(',', '')
        return num2words(clean_val, lang='vi').capitalize()
    except:
        return str(value)

def dateformat_filter(value, fmt="%d/%m/%Y"):
    """Định dạng ngày tháng"""
    if not value: return ""
    if isinstance(value, str):
        try:
            # Thử parse string 'YYYY-MM-DD' sang date object
            value = datetime.strptime(value, '%Y-%m-%d')
        except:
            return value
    if isinstance(value, (datetime,)):
        return value.strftime(fmt)
    return str(value)
# -----------------------------------------------------
# 1.1 ViewSet cho FieldGroup (MỚI)
class FieldGroupViewSet(viewsets.ModelViewSet):
    queryset = FieldGroup.objects.all().order_by('order')
    serializer_class = FieldGroupSerializer
    # Chỉ Admin mới được đụng vào cấu hình này
    # permission_classes = [IsAdminUser] # Tạm thời để AllowAny nếu chưa làm login, nhưng nên là IsAdminUser
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
    permission_classes = [AllowAny]  # Để test



    @action(detail=False, methods=['get'])
    def active_fields_grouped(self, request):
        """Trả về danh sách trường active nhóm theo FieldGroup"""
        # Lấy tất cả các nhóm, sắp xếp theo thứ tự
        groups = FieldGroup.objects.all().order_by('order').prefetch_related(
            Prefetch('fields', queryset=Field.objects.filter(is_active=True))
        )

        result = {}
        for grp in groups:
            # Chỉ lấy nhóm nào có trường dữ liệu
            fields_data = FieldSerializer(grp.fields.all(), many=True).data  # Ensure related_name='fields' is correct
            if fields_data:
                result[grp.name] = fields_data  # Frontend sẽ dùng key là tên nhóm để hiển thị tiêu đề

        # Add synthetic fields to the grouped response
        result["Thông tin cá nhân"] = [] # Clear synthetic fields

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
                # A. Cập nhật thông tin cơ bản
                if 'name' in data:
                    loan_profile.name = data['name']
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
                        else:
                            # Nếu không thấy, tạo mới (Person giờ chỉ là ID holder)
                            person = Person.objects.create()
                    else:
                        # Nếu không có CCCD, tạo mới luôn
                        person = Person.objects.create()

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
                                defaults={'value': str(val)}
                            )
                        except Field.DoesNotExist:
                            continue

                # D. Dọn dẹp (Xóa những người bị remove khỏi form)
                LoanProfilePerson.objects.filter(loan_profile=loan_profile).exclude(
                    person__id__in=current_person_ids).delete()
                FieldValue.objects.filter(loan_profile=loan_profile, person__isnull=False).exclude(
                    person__id__in=current_person_ids).delete()

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
        context['ngay_tao'] = loan_profile.created_at.strftime("%d/%m/%Y")

        # B. Các trường chung (FieldValues không gắn với Person)
        # Biến đổi từ: {field: "so_tien", value: "100"} -> context["so_tien"] = "100"
        general_fvs = loan_profile.fieldvalue_set.filter(person__isnull=True)
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
                'cccd_so': get_val('cccd_so'),
                'roles': link.roles,  # Mảng các vai trò
            }
            for fv in person_fvs:
                p_data[fv.field.placeholder_key] = fv.value

            people_list.append(p_data)

        context['people'] = people_list

        # D. Tạo các danh sách lọc sẵn để tiện dùng trong Word
        # Lọc những người có vai trò 'Bên Vay'
        context['ben_vay_list'] = [p for p in people_list if 'Bên Vay' in p['roles']]
        # Lọc những người có vai trò 'Bên Bảo đảm'
        context['ben_bao_dam_list'] = [p for p in people_list if 'Bên Bảo đảm' in p['roles']]

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