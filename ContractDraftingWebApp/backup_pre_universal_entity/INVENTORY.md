# Backup Inventory - Pre Universal Entity Migration

**Generated**: 2025-12-31 15:30  
**Total Files**: 33 (Backend: 28, Frontend: 5)

## Backend Files (Django App)

### Migrations (22 files)
- `0001_initial.py` - 4,973 bytes - Initial database schema
- `0002_documenttemplate.py` - 1,045 bytes - Document templates
- `0003_person_cccd_so.py` - 475 bytes - Person CCCD field
- `0004_fieldgroup_alter_fieldvalue_options_and_more.py` - 4,698 bytes - Field groups
- `0005_remove_field_group_name_field_group.py` - 706 bytes
- `0006_field_note_fieldgroup_note_and_more.py` - 1,485 bytes
- `0007_alter_fieldgroup_options_alter_person_id.py` - 632 bytes
- `0008_remove_person_cccd_so_remove_person_name_for_display.py` - 497 bytes
- `0009_role.py` - 878 bytes - Role model
- `0010_field_css_class_field_order_field_width_cols.py` - 840 bytes
- `0011_asset_alter_fieldvalue_unique_together_and_more.py` - 1,992 bytes - Asset model
- `0012_add_is_protected_to_field.py` - 510 bytes
- `0013_add_default_value_to_field.py` - 476 bytes
- `0014_alter_field_data_type.py` - 616 bytes
- `0015_formview_field_allowed_forms_and_more.py` - 1,466 bytes
- `0016_loanprofile_form_view.py` - 598 bytes
- `0017_role_slug.py` - 490 bytes
- `0018_field_use_digit_grouping.py` - 476 bytes
- `0019_field_show_amount_in_words.py` - 494 bytes
- `0020_asset_created_at_asset_updated_at_person_created_at_and_more.py` - 972 bytes
- `0021_asset_last_updated_by_person_last_updated_by.py` - 995 bytes
- `0022_fieldgroup_entity_type_alter_fieldvalue_loan_profile.py` - 925 bytes

### Core Application Files
- `models_backup.py` - 9,683 bytes - Person, Asset, LoanProfile models
- `serializers_backup.py` - 12,153 bytes - All serializers including Master Data
- `views_backup.py` - 37,871 bytes - ViewSets and save_form_data logic
- `urls_backup.py` - 914 bytes - API routing
- `admin_backup.py` - 2,796 bytes - Django admin configuration

### Reference Files
- `schema_initial.sql` - 7,990 bytes - SQL schema dump
- `migration_list.txt` - 3,654 bytes - Migration file listing

## Frontend Files (Vue.js Components)

Located in `frontend_backup/` subdirectory:

- `PersonForm.vue` - Person data entry form with roles
- `AssetForm.vue` - Asset data entry form
- `LoanProfileForm.vue` - Main profile form (split-panel: people left, assets right)
- `MasterData.vue` - Master data management with tabs for People/Assets
- `MasterCreateModal.vue` - Dynamic entity creation modal

## Key Architecture Features (Backed Up)

### Backend
- ✅ Separate `Person` and `Asset` models
- ✅ `LoanProfilePerson` junction with `roles` field (ArrayField)
- ✅ `LoanProfileAsset` junction without roles
- ✅ `FieldValue` with separate FKs to `person` and `asset`
- ✅ `MasterPersonViewSet` and `MasterAssetViewSet` as separate endpoints
- ✅ Complex `save_form_data` logic handling Person/Asset separately

### Frontend
- ✅ Separate PersonForm and AssetForm components
- ✅ LoanProfileForm with hardcoded split: people (left) + assets (right)
- ✅ Master Data view with hardcoded tabs for 'people' and 'assets'
- ✅ Role selection UI only in PersonForm

## Total Backup Size
Approximately **88 KB** of critical source code

---

**Note**: This inventory serves as a quick reference for what's included in the backup. See `README.md` for detailed rollback procedures.
