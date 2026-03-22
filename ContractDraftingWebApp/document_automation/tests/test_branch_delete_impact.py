"""
Test: Ảnh hưởng của việc xóa mềm/cứng BRANCH đến UserProfile và sinh hợp đồng.

Kịch bản:
- User 'test_branch_user' có profile.branch = BRANCH object
- Kiểm tra hành vi sau khi soft-delete và hard-delete BRANCH đó
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.utils import timezone

from document_automation.models import (
    MasterObject, MasterObjectType, FieldValue, Field, FieldGroup,
    UserProfile, LoanProfile, LoanProfileObjectLink
)


class BranchDeleteImpactTest(TestCase):
    """Kiểm tra ảnh hưởng của xóa mềm/cứng BRANCH đến profile và sinh hợp đồng."""

    def setUp(self):
        """Tạo dữ liệu test: User, BRANCH, Field, FieldValue, LoanProfile."""
        # 1. Tạo MasterObjectType BRANCH (nếu chưa có)
        self.branch_type, _ = MasterObjectType.objects.get_or_create(
            code='BRANCH',
            defaults={
                'name': 'Chi nhánh',
                'identity_field_key': 'ten_chi_nhanh',
                'is_system': True,
            }
        )

        # 2. Tạo Field Group và Field cho BRANCH
        self.branch_group, _ = FieldGroup.objects.get_or_create(
            slug='branch_info',
            defaults={'name': 'Thông tin chi nhánh', 'entity_type': 'PROFILE'}
        )
        self.field_ten_cn, _ = Field.objects.get_or_create(
            placeholder_key='ten_chi_nhanh',
            defaults={'label': 'Tên chi nhánh', 'group': self.branch_group}
        )
        self.field_dia_chi_cn, _ = Field.objects.get_or_create(
            placeholder_key='dia_chi_chi_nhanh',
            defaults={'label': 'Địa chỉ chi nhánh', 'group': self.branch_group}
        )

        # 3. Tạo BRANCH object
        self.branch = MasterObject.objects.create(object_type='BRANCH')
        FieldValue.objects.create(
            master_object=self.branch, field=self.field_ten_cn,
            value='CN Thủ Đức Test', loan_profile=None
        )
        FieldValue.objects.create(
            master_object=self.branch, field=self.field_dia_chi_cn,
            value='123 Võ Văn Ngân, TP.HCM', loan_profile=None
        )

        # 4. Tạo User và gán branch
        self.user = User.objects.create_user('test_branch_user', 'test@test.com', 'password123')
        self.user.profile.branch = self.branch
        self.user.profile.save()

        # 5. Tạo LoanProfile để test sinh hợp đồng
        self.loan_profile = LoanProfile.objects.create(
            name='Hồ sơ test branch delete',
            created_by_user=self.user
        )

    # =========================================================================
    # TÌNH HUỐNG 1: XÓA MỀM (SOFT DELETE) - Ảnh hưởng lên Profile
    # =========================================================================

    def test_soft_delete_branch_profile_still_has_branch(self):
        """Xóa mềm BRANCH → profile.branch_id vẫn intact."""
        # ACT: Soft delete
        self.branch.deleted_at = timezone.now()
        self.branch.save()

        # ASSERT: Profile vẫn giữ FK
        self.user.profile.refresh_from_db()
        self.assertEqual(self.user.profile.branch_id, self.branch.id)
        self.assertIsNotNone(self.user.profile.branch)

    def test_soft_delete_branch_serializer_returns_data(self):
        """Xóa mềm BRANCH → UserSerializer vẫn trả branch_name đúng."""
        # ACT
        self.branch.deleted_at = timezone.now()
        self.branch.save()

        # ASSERT
        from document_automation.serializers import UserSerializer
        serializer = UserSerializer(self.user)
        data = serializer.data
        self.assertEqual(data['branch_id'], self.branch.id)
        self.assertIsNotNone(data['branch_name'])
        self.assertIn('Thủ Đức', data['branch_name'])

    # =========================================================================
    # TÌNH HUỐNG 2: XÓA CỨNG (HARD DELETE) - Ảnh hưởng lên Profile
    # =========================================================================

    def test_hard_delete_branch_profile_becomes_null(self):
        """Xóa cứng BRANCH → on_delete=SET_NULL → profile.branch_id = None."""
        # ACT: Hard delete
        self.branch.delete()

        # ASSERT
        self.user.profile.refresh_from_db()
        self.assertIsNone(self.user.profile.branch_id)
        self.assertIsNone(self.user.profile.branch)

    def test_hard_delete_serializer_returns_null(self):
        """Xóa cứng BRANCH → API trả branch_id: null, branch_name: null."""
        # ACT
        self.branch.delete()

        # ASSERT
        self.user.refresh_from_db()
        from document_automation.serializers import UserSerializer
        serializer = UserSerializer(self.user)
        data = serializer.data
        self.assertIsNone(data['branch_id'])
        self.assertIsNone(data['branch_name'])

    # =========================================================================
    # TÌNH HUỐNG 3: XÓA MỀM - Ảnh hưởng lên sinh hợp đồng
    # =========================================================================

    def test_soft_delete_branch_document_context_has_data(self):
        """Xóa mềm BRANCH → current_branch trong context vẫn có data đầy đủ."""
        # ACT
        self.branch.deleted_at = timezone.now()
        self.branch.save()

        from document_automation.services.document_service import DocumentService
        context = DocumentService.prepare_context(self.loan_profile, user=self.user)

        # ASSERT: current_branch phải là dict không rỗng
        current_branch = context.get('current_branch', {})
        self.assertIsInstance(current_branch, dict)
        self.assertTrue(len(current_branch) > 0, "current_branch phải có dữ liệu sau xóa mềm")
        self.assertEqual(current_branch.get('ten_chi_nhanh'), 'CN Thủ Đức Test')
        self.assertEqual(current_branch.get('dia_chi_chi_nhanh'), '123 Võ Văn Ngân, TP.HCM')

    # =========================================================================
    # TÌNH HUỐNG 4: XÓA CỨNG - Ảnh hưởng lên sinh hợp đồng
    # =========================================================================

    def test_hard_delete_branch_document_context_empty(self):
        """Xóa cứng BRANCH → current_branch = {} (rỗng) → MẤT thông tin chi nhánh."""
        # ACT
        self.branch.delete()

        self.user.profile.refresh_from_db()
        from document_automation.services.document_service import DocumentService
        context = DocumentService.prepare_context(self.loan_profile, user=self.user)

        # ASSERT: current_branch phải rỗng
        current_branch = context.get('current_branch', {})
        self.assertIsInstance(current_branch, dict)
        self.assertEqual(len(current_branch), 0, "current_branch phải rỗng sau xóa cứng")


class BranchDeleteFrontendBehaviorTest(TestCase):
    """Kiểm tra hành vi API list BRANCH sau xóa mềm/cứng (ảnh hưởng đến frontend dropdown)."""

    def setUp(self):
        self.admin = User.objects.create_superuser('admin_branch_test', 'admin@test.com', 'Admin@123456')
        self.client.force_login(self.admin)

        # Tạo MasterObjectType BRANCH
        MasterObjectType.objects.get_or_create(
            code='BRANCH',
            defaults={'name': 'Chi nhánh', 'identity_field_key': 'ten_chi_nhanh', 'is_system': True}
        )

        # Tạo 2 BRANCH
        self.branch_a = MasterObject.objects.create(object_type='BRANCH')
        self.branch_b = MasterObject.objects.create(object_type='BRANCH')

    def test_soft_deleted_branch_still_in_list(self):
        """Xóa mềm → BRANCH vẫn xuất hiện trong API list (frontend dropdown vẫn thấy)."""
        # ACT
        self.branch_a.deleted_at = timezone.now()
        self.branch_a.save()

        from django.urls import reverse
        url = reverse('master-objects-list')
        response = self.client.get(url, {'object_type': 'BRANCH'})

        # ASSERT
        self.assertEqual(response.status_code, 200)
        data = response.data
        results = data.get('results', data) if isinstance(data, dict) else data
        ids = [item['id'] for item in results]

        # Branch A (soft-deleted) VẪN trong danh sách
        self.assertIn(self.branch_a.id, ids, "Branch xóa mềm phải vẫn xuất hiện trong list API")
        # Branch B bình thường
        self.assertIn(self.branch_b.id, ids)

    def test_hard_deleted_branch_gone_from_list(self):
        """Xóa cứng → BRANCH biến mất hoàn toàn khỏi API list (frontend dropdown không thấy)."""
        branch_a_id = self.branch_a.id

        # ACT
        self.branch_a.delete()

        from django.urls import reverse
        url = reverse('master-objects-list')
        response = self.client.get(url, {'object_type': 'BRANCH'})

        # ASSERT
        self.assertEqual(response.status_code, 200)
        data = response.data
        results = data.get('results', data) if isinstance(data, dict) else data
        ids = [item['id'] for item in results]

        # Branch A (hard-deleted) KHÔNG CÒN trong danh sách
        self.assertNotIn(branch_a_id, ids, "Branch xóa cứng phải biến mất khỏi list API")
        # Branch B vẫn còn
        self.assertIn(self.branch_b.id, ids)
