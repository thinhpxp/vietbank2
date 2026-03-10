from django.conf import settings
from django.utils import timezone
from docxtpl import DocxTemplate
from jinja2 import Environment
import io
import os
import zipfile
import logging
from datetime import datetime, date

from ..models import Field, FieldValue, MasterObject, MasterObjectRelation, Role, MasterObjectType, DocumentTemplate
from ..views.export_views import (
    format_currency_filter, num2words_filter, dateformat_filter, 
    to_roman_filter, evaluate_formula, clean_filename
)

logger = logging.getLogger(__name__)

class DocumentService:
    @staticmethod
    def prepare_context(loan_profile):
        """
        Chuẩn bị dữ liệu context tập hợp từ Hồ sơ vay để trộn vào Template.
        """
        loan_profile.refresh_from_db()
        context = {'ten_ho_so': loan_profile.name}
        
        # 1. Ngày lập hồ sơ
        ngay_lap_fv = FieldValue.objects.filter(
            loan_profile=loan_profile, 
            field__placeholder_key='ngay_lap_ho_so', 
            master_object__isnull=True
        ).first()
        context['ngay_tao'] = ngay_lap_fv.value if ngay_lap_fv and ngay_lap_fv.value else loan_profile.created_at

        # 2. Các trường dữ liệu chung
        for fv in FieldValue.objects.filter(loan_profile=loan_profile, master_object__isnull=True):
            context[fv.field.placeholder_key] = fv.value

        # 3. Helper lấy quan hệ của đối tượng
        def get_relations(mo_id):
            relations = {
                'related_assets': [], 'related_people': [], 
                'base_contracts': [], 'amending_contracts': [], 
                'secured_loan_contracts': [], 'contracts_securing': []
            }
            # Output relations
            for r in MasterObjectRelation.objects.filter(source_object_id=mo_id).select_related('target_object'):
                d = {'id': r.target_object.id, 'object_type': r.target_object.object_type, 'relation_type': r.relation_type}
                d.update({fv.field.placeholder_key: fv.value 
                         for fv in FieldValue.objects.filter(master_object=r.target_object, loan_profile__isnull=True)})
                relations['related_assets'].append(d)
                if r.relation_type == 'AMENDS': relations['base_contracts'].append(d)
                if r.relation_type == 'SECURES': relations['secured_loan_contracts'].append(d)
            # Input relations
            for r in MasterObjectRelation.objects.filter(target_object_id=mo_id).select_related('source_object'):
                d = {'id': r.source_object.id, 'object_type': r.source_object.object_type, 'relation_type': r.relation_type}
                d.update({fv.field.placeholder_key: fv.value 
                         for fv in FieldValue.objects.filter(master_object=r.source_object, loan_profile__isnull=True)})
                relations['related_people'].append(d)
                if r.relation_type == 'AMENDS': relations['amending_contracts'].append(d)
                if r.relation_type == 'SECURES': relations['contracts_securing'].append(d)
            return relations

        # 4. Danh sách People
        from ..models import LoanProfileObjectLink
        people_list = []
        for link in LoanProfileObjectLink.objects.filter(loan_profile=loan_profile, master_object__object_type='PERSON').select_related('master_object'):
            p = {'id': link.master_object.id, 'roles': link.roles}
            p.update({fv.field.placeholder_key: fv.value 
                     for fv in FieldValue.objects.filter(loan_profile=loan_profile, master_object=link.master_object)})
            p.update(get_relations(link.master_object.id))
            people_list.append(p)
        context['people'] = people_list

        # 5. Danh sách Assets (and other non-person objects)
        assets_list = []
        for link in LoanProfileObjectLink.objects.filter(loan_profile=loan_profile).exclude(master_object__object_type='PERSON').select_related('master_object'):
            a = {'id': link.master_object.id, '_object_type': link.master_object.object_type}
            a.update({fv.field.placeholder_key: fv.value 
                     for fv in FieldValue.objects.filter(loan_profile=loan_profile, master_object=link.master_object)})
            a.update(get_relations(link.master_object.id))
            assets_list.append(a)
        context['assets'] = assets_list

        # 6. Grouping by object type
        for a in assets_list:
            ot = a.get('_object_type')
            if ot:
                if ot not in context: context[ot] = []
                context[ot].append(a)
                sk = f"{ot.lower()}_list"
                if sk not in context: context[sk] = []
                context[sk].append(a)

        # 7. Flattening Dedicated Sections
        dedicated_codes = MasterObjectType.objects.filter(form_display_mode='DEDICATED_SECTION').values_list('code', flat=True)
        reserved = ['ten_ho_so', 'ngay_tao', 'people', 'assets', 'tin_dung_list', 'bao_dam_list']
        for tc in dedicated_codes:
            items = context.get(tc, [])
            if items:
                for k, v in items[0].items():
                    if k not in reserved: context[k] = v

        # 8. Role-based filtering
        all_sys_roles = Role.objects.exclude(slug__isnull=True).exclude(slug='')
        role_map = {r.name.strip().lower(): r.slug.strip().lower() for r in all_sys_roles}
        legacy_map = {'ben_vay': ['bên vay', 'bên được cấp tín dụng'], 'ben_duoc_cap_tin_dung': ['bên được cấp tín dụng'], 'ben_the_chap': ['bên thế chấp', 'bên bảo đảm'], 'ben_bao_dam': ['bên bảo đảm'], 'ben_bao_lanh': ['bên bảo lãnh']}
        role_lists = {s: [] for s in (set(role_map.values()) | set(legacy_map.keys()))}
        for p in people_list:
            matched = set()
            for rname in [r.strip().lower() for r in p.get('roles', [])]:
                if rname in role_map: matched.add(role_map[rname])
                for ls, lnames in legacy_map.items():
                    if rname in lnames: matched.add(ls)
            for m in matched: role_lists[m].append(p)
        for s, pl in role_lists.items(): context[f"{s}_list"] = pl
        
        if 'ben_vay_list' in context: context['tin_dung_list'] = context['ben_vay_list']
        if 'ben_bao_dam_list' in context: context['bao_dam_list'] = context['ben_bao_dam_list']

        # 9. Computed Fields
        for cf in Field.objects.filter(is_active=True, default_value__startswith='='):
            res = evaluate_formula(cf.default_value, context)
            if res is not None: context[cf.placeholder_key] = res

        context['today'] = date.today().strftime('%d/%m/%Y')
        return context

    @staticmethod
    def generate_documents(loan_profile, template_ids, export_mode='SINGLE', batch_template_ids=None, target_object_id=None):
        """
        Sinh danh sách các file văn bản từ danh sách mã mẫu.
        """
        if not batch_template_ids: batch_template_ids = []
        context = DocumentService.prepare_context(loan_profile)
        
        jinja_env = Environment()
        jinja_env.filters.update({
            'format_currency': format_currency_filter, 
            'num2words': num2words_filter, 
            'dateformat': dateformat_filter, 
            'to_roman': to_roman_filter
        })

        templates = DocumentTemplate.objects.filter(id__in=template_ids)
        results, errors = [], []

        for temp in templates:
            eff_batch = (export_mode == 'BATCH') or (temp.id in batch_template_ids)
            try:
                if not os.path.exists(temp.file.path): continue
                if eff_batch and temp.loop_object_type:
                    ltype = temp.loop_object_type.code
                    ikey = temp.loop_object_type.identity_field_key
                    objs = context.get(ltype, []) or context.get(ltype.lower(), [])
                    if target_object_id: 
                        objs = [o for o in objs if str(o.get('id')) == str(target_object_id)]
                    
                    for obj in objs:
                        b_ctx = context.copy()
                        b_ctx.update({'current_asset': obj, 'current_object': obj, 'is_batch': True, 'is_single': False})
                        b_ctx.update({k: v for k, v in obj.items() if not k.startswith('_')})
                        doc = DocxTemplate(temp.file.path)
                        doc.render(b_ctx, jinja_env=jinja_env)
                        stream = io.BytesIO()
                        doc.save(stream)
                        stream.seek(0)
                        ident = obj.get(ikey) or obj.get('id', 'unknown')
                        results.append((f"{clean_filename(temp.name)}_{clean_filename(str(ident))}.docx", stream))
                else:
                    s_ctx = context.copy()
                    s_ctx.update({'is_batch': False, 'is_single': True})
                    if temp.loop_object_type:
                        ot_list = context.get(temp.loop_object_type.code, []) or context.get(temp.loop_object_type.code.lower(), [])
                        if ot_list:
                            s_ctx.update({'current_asset': ot_list[0], 'current_object': ot_list[0]})
                            s_ctx.update({k: v for k, v in ot_list[0].items() if not k.startswith('_')})
                    doc = DocxTemplate(temp.file.path)
                    doc.render(s_ctx, jinja_env=jinja_env)
                    stream = io.BytesIO()
                    doc.save(stream)
                    stream.seek(0)
                    results.append((f"{clean_filename(temp.name)}.docx", stream))
            except Exception as ex:
                logger.error(f"Error rendering template {temp.id}: {ex}")
                errors.append(f"Mẫu {temp.name}: {str(ex)}")

        return results, errors
