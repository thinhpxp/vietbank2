# Complete Backup & Rollback Guide - Pre Universal Entity Migration

**Backup Date**: 2025-12-31 15:30  
**Purpose**: Full backup before transitioning to Universal Entity architecture  
**Backup Location**: `ContractDraftingWebApp\backup_pre_universal_entity\`

---

## 📦 Backup Contents

### Backend (Django)
- ✅ **All 22 migration files** - Complete database evolution history
- ✅ **models.py** - Person, Asset, LoanProfile, FieldValue models
- ✅ **serializers.py** - PersonSerializer, AssetSerializer, MasterPersonSerializer, etc.
- ✅ **views.py** - All ViewSets including save_form_data logic
- ✅ **urls.py** - API routing configuration
- ✅ **admin.py** - Django admin configuration (if exists)
- ✅ **schema_initial.sql** - SQL dump of initial schema

### Frontend (Vue.js)
- ✅ **PersonForm.vue** - Person data entry component
- ✅ **AssetForm.vue** - Asset data entry component
- ✅ **LoanProfileForm.vue** - Main profile form with Person/Asset lists
- ✅ **MasterData.vue** - Master data management view
- ✅ **MasterCreateModal.vue** - Entity creation modal

---

## 🔄 Complete Rollback Procedure

If you need to restore the original Person/Asset architecture, follow these steps **in order**:

### Step 1: Stop Running Services
```powershell
# Stop Django dev server (Ctrl+C in terminal)
# Stop Vue dev server (Ctrl+C in terminal)
```

### Step 2: Restore Backend Files

```powershell
cd c:\Users\thinhpxp\Webapp_vietbank\ContractDraftingWebApp

# Restore models
Copy-Item -Path ".\backup_pre_universal_entity\models_backup.py" -Destination ".\document_automation\models.py" -Force

# Restore serializers
Copy-Item -Path ".\backup_pre_universal_entity\serializers_backup.py" -Destination ".\document_automation\serializers.py" -Force

# Restore views
Copy-Item -Path ".\backup_pre_universal_entity\views_backup.py" -Destination ".\document_automation\views.py" -Force

# Restore URLs
Copy-Item -Path ".\backup_pre_universal_entity\urls_backup.py" -Destination ".\document_automation\urls.py" -Force

# Restore admin (if exists)
Copy-Item -Path ".\backup_pre_universal_entity\admin_backup.py" -Destination ".\document_automation\admin.py" -Force -ErrorAction SilentlyContinue
```

### Step 3: Restore Migrations

```powershell
# Delete all current migrations (keep __init__.py)
Remove-Item ".\document_automation\migrations\*.py" -Exclude "__init__.py"

# Copy back original migrations
Copy-Item -Path ".\backup_pre_universal_entity\*.py" -Destination ".\document_automation\migrations\" -Exclude "*_backup.py"
```

### Step 4: Reset Database Schema

```powershell
# Reset migrations to zero (clears all tables)
.\venv\Scripts\python.exe manage.py migrate document_automation zero

# Re-apply all migrations
.\venv\Scripts\python.exe manage.py migrate document_automation

# Verify migration status
.\venv\Scripts\python.exe manage.py showmigrations document_automation
```

### Step 5: Restore Frontend Components

```powershell
cd c:\Users\thinhpxp\Webapp_vietbank\frontend

# Restore Person form
Copy-Item -Path "..\ContractDraftingWebApp\backup_pre_universal_entity\frontend_backup\PersonForm.vue" -Destination ".\src\components\PersonForm.vue" -Force

# Restore Asset form
Copy-Item -Path "..\ContractDraftingWebApp\backup_pre_universal_entity\frontend_backup\AssetForm.vue" -Destination ".\src\components\AssetForm.vue" -Force

# Restore LoanProfileForm
Copy-Item -Path "..\ContractDraftingWebApp\backup_pre_universal_entity\frontend_backup\LoanProfileForm.vue" -Destination ".\src\views\LoanProfileForm.vue" -Force

# Restore MasterData view
Copy-Item -Path "..\ContractDraftingWebApp\backup_pre_universal_entity\frontend_backup\MasterData.vue" -Destination ".\src\views\admin\MasterData.vue" -Force

# Restore MasterCreateModal
Copy-Item -Path "..\ContractDraftingWebApp\backup_pre_universal_entity\frontend_backup\MasterCreateModal.vue" -Destination ".\src\components\MasterCreateModal.vue" -Force
```

### Step 6: Verify and Restart

```powershell
# Backend - Check for syntax errors
cd c:\Users\thinhpxp\Webapp_vietbank\ContractDraftingWebApp
.\venv\Scripts\python.exe manage.py check

# Frontend - Check for lint errors
cd c:\Users\thinhpxp\Webapp_vietbank\frontend
npm run lint

# Start servers
# Terminal 1: python manage.py runserver
# Terminal 2: npm run serve
```

### Step 7: Reconfigure Data (Optional)

After rollback, you may need to:
- ✅ Recreate FieldGroups configuration via Admin
- ✅ Recreate custom Roles
- ✅ Import sample data if needed

---

## 🔍 What Gets Rolled Back

| Component | Rollback Effect |
|:---|:---|
| Database Schema | Separate `Person` and `Asset` tables restored |
| Junction Tables | `LoanProfilePerson` (with roles) and `LoanProfileAsset` (no roles) |
| Field Values | FK to `person` or `asset` instead of generic `object` |
| Backend Logic | Hardcoded Person/Asset handling in save_form_data |
| API Endpoints | `/api/master-people/` and `/api/master-assets/` as separate |
| Frontend Forms | Separate PersonForm.vue and AssetForm.vue components |
| Roles System | Only applicable to Person entities |

---

## ⚠️ Important Notes

1. **Data Loss**: Rollback will **delete all data** in LoanProfile, Person, Asset tables
2. **Manual Work**: You'll need to reconfigure FieldGroups and Roles after rollback
3. **Testing**: Always test in development before rolling back production
4. **Timing**: The entire rollback takes approximately 5-10 minutes

---

## 📞 Troubleshooting

### If migrations fail:
```powershell
# Hard reset (WARNING: deletes all data)
.\venv\Scripts\python.exe manage.py migrate document_automation zero --fake
.\venv\Scripts\python.exe manage.py migrate document_automation --fake-initial
```

### If frontend has errors:
```powershell
# Clear node cache
rm -rf node_modules
npm install
npm run serve
```

### If database is corrupted:
Use Supabase dashboard to drop all tables manually, then re-run migrations.

---

## ✅ Verification Checklist

After rollback, verify:
- [ ] Django server starts without errors
- [ ] Frontend compiles without errors
- [ ] Can create new LoanProfile
- [ ] Can add Person with roles
- [ ] Can add Asset
- [ ] Master Data view shows Person and Asset tabs
- [ ] Field values save correctly

---

**Last Updated**: 2025-12-31 15:30  
**By**: Antigravity AI Assistant
