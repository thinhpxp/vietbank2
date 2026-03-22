import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ContractDraftingWebApp.settings")
django.setup()

from document_automation.models import MasterObject, FieldValue
from document_automation.serializers import MasterObjectLiteSerializer
import traceback

print("Executing search logic...")
query = "Hồ"

matching_master_ids = FieldValue.objects.filter(
    master_object__isnull=False,
    loan_profile__isnull=True,
    value__icontains=query
).values_list('master_object_id', flat=True).distinct()

qs = MasterObject.objects.filter(id__in=matching_master_ids, deleted_at__isnull=True)
qs = qs[:20]

serializer = MasterObjectLiteSerializer(qs, many=True)
try:
    data = serializer.data
    print("Success! Return length:", len(data))
except Exception as e:
    traceback.print_exc()
