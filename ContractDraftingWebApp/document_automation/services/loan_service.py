from django.utils import timezone
from django.db import transaction
from django.db.models import Q
import logging

from ..models import (
    LoanProfile, Field, FieldValue, FormView, MasterObject, 
    LoanProfileObjectLink, MasterObjectRelation, Role
)
from ..views.system_views import log_action
from ..views.master_views import find_existing_master_object, save_master_field_values

logger = logging.getLogger(__name__)

class LoanService:
    @staticmethod
    def duplicate_profile(profile_id, new_name, user):
        """Sao chép hồ sơ vay và toàn bộ dữ liệu liên quan"""
        original = LoanProfile.objects.get(id=profile_id)
        if not new_name:
            new_name = f"Bản sao - {original.name}"
            
        try:
            with transaction.atomic():
                new_profile = LoanProfile.objects.create(
                    name=new_name, 
                    form_view=original.form_view, 
                    created_by_user=user
                )
                
                # Sao chép FieldValues chung
                for fv in original.fieldvalue_set.filter(master_object__isnull=True):
                    FieldValue.objects.create(loan_profile=new_profile, field=fv.field, value=fv.value)
                
                # Sao chép Links và FieldValues liên quan đối tượng
                for link in original.object_links.all():
                    LoanProfileObjectLink.objects.create(
                        loan_profile=new_profile, 
                        master_object=link.master_object, 
                        roles=link.roles
                    )
                    for fv in original.fieldvalue_set.filter(master_object=link.master_object):
                        FieldValue.objects.create(
                            loan_profile=new_profile, 
                            master_object=link.master_object, 
                            field=fv.field, 
                            value=fv.value
                        )
                return new_profile
        except Exception as e:
            logger.error(f"Error duplicating profile: {e}")
            raise e

    @staticmethod
    def save_loan_form_data(loan_profile, data, user):
        """Xử lý lưu dữ liệu từ dynamic form vào hồ sơ"""
        is_auto_save = str(data.get('is_auto_save', 'False')).lower() == 'true'
        
        try:
            with transaction.atomic():
                # A. Cập nhật thông tin cơ bản
                if 'name' in data:
                    loan_profile.name = data['name']
                
                form_slug = data.get('form_slug')
                if form_slug:
                    form_v = FormView.objects.filter(slug=form_slug).first()
                    if form_v: loan_profile.form_view = form_v
                loan_profile.save()

                # B. Lưu FieldValues chung
                for key, val in data.get('field_values', {}).items():
                    try:
                        field_obj = Field.objects.get(placeholder_key=key)
                        FieldValue.objects.update_or_create(
                            loan_profile=loan_profile, 
                            master_object=None, 
                            field=field_obj, 
                            defaults={'value': str(val) if val is not None else ""}
                        )
                    except Field.DoesNotExist: continue

                # C. Xử lý Objects (People, Assets)
                processed_master_ids = []
                
                def process_objects(data_list, default_obj_type):
                    for item_data in data_list:
                        obj_id = item_data.get('id')
                        roles = item_data.get('roles', [])
                        fields_dict = item_data.get('individual_field_values') or item_data.get('asset_field_values', {})
                        
                        actual_type = default_obj_type
                        if 'master_object' in item_data and item_data['master_object']:
                            actual_type = item_data['master_object'].get('object_type', default_obj_type)
                            
                        if not obj_id and (not actual_type or not any(str(v).strip() for v in fields_dict.values() if v)):
                            continue
                            
                        master_obj = MasterObject.objects.filter(id=obj_id).first() if obj_id else find_existing_master_object(actual_type, fields_dict)
                        
                        if not master_obj:
                            master_obj = MasterObject.objects.create(
                                object_type=actual_type, 
                                last_updated_by=user, 
                                is_draft=is_auto_save
                            )
                            save_master_field_values(master_obj, fields_dict)
                            
                        if not is_auto_save and getattr(master_obj, 'is_draft', False):
                            master_obj.is_draft = False
                            master_obj.save(update_fields=['is_draft'])
                            
                        processed_master_ids.append(master_obj.id)
                        
                        LoanProfileObjectLink.objects.update_or_create(
                            loan_profile=loan_profile, 
                            master_object=master_obj, 
                            defaults={'roles': roles}
                        )
                        
                        for f_key, f_val in fields_dict.items():
                            try:
                                f_obj = Field.objects.get(placeholder_key=f_key)
                                if f_obj.allowed_object_types.exists() and actual_type not in f_obj.allowed_object_types.values_list('code', flat=True):
                                    continue
                                FieldValue.objects.update_or_create(
                                    loan_profile=loan_profile, 
                                    master_object=master_obj, 
                                    field=f_obj, 
                                    defaults={'value': str(f_val)}
                                )
                            except Field.DoesNotExist: continue

                # D. Điều phối xử lý các section
                object_sections = data.get('object_sections', {})
                if object_sections:
                    for t_code, items in object_sections.items():
                        process_objects(items, t_code)
                else:
                    process_objects(data.get('people', []), 'PERSON')
                    process_objects(data.get('attorneys', []), 'ATTORNEY')
                    process_objects(data.get('assets', []), 'ASSET')

                # E. Dọn dẹp các link cũ không còn trong payload
                LoanProfileObjectLink.objects.filter(loan_profile=loan_profile).exclude(master_object__id__in=processed_master_ids).delete()
                
                # F. Tự động suy luận quan hệ (Relation Inference)
                LoanService.infer_relations(loan_profile)
                
                # G. Dọn dẹp FieldValues mồ côi
                FieldValue.objects.filter(loan_profile=loan_profile, master_object__isnull=False).exclude(master_object__id__in=processed_master_ids).delete()

                if not is_auto_save:
                    log_action(user, 'UPDATE', 'LoanProfile', loan_profile.id, f"Cập nhật dữ liệu từ Form: {loan_profile.name}")
                
                return loan_profile
        except Exception as e:
            logger.error(f"Error saving loan form data: {e}")
            raise e

    @staticmethod
    def infer_relations(loan_profile):
        """Tự động tạo quan hệ giữa Người và Tài sản dựa trên vai trò"""
        profile_links = LoanProfileObjectLink.objects.filter(loan_profile=loan_profile).select_related('master_object')
        potential_owners = []
        system_roles = Role.objects.exclude(relation_type__isnull=True).exclude(relation_type='')
        
        for link in profile_links:
            if link.master_object.object_type == 'PERSON' and link.roles:
                for role_str in link.roles:
                    matching_role = next((r for r in system_roles if r.slug == role_str or r.name == role_str), None)
                    if matching_role:
                        potential_owners.append({'person': link.master_object, 'relation': matching_role.relation_type})
        
        assets_in_profile = [link.master_object for link in profile_links if link.master_object.object_type != 'PERSON']
        
        if potential_owners and assets_in_profile:
            for owner_data in potential_owners:
                for asset in assets_in_profile:
                    MasterObjectRelation.objects.get_or_create(
                        source_object=owner_data['person'], 
                        target_object=asset, 
                        relation_type=owner_data['relation']
                    )
