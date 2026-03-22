from document_automation.models import MasterObject
from document_automation.serializers import MasterObjectLiteSerializer
import traceback

qs = MasterObject.objects.all()[:2]
serializer = MasterObjectLiteSerializer(qs, many=True)
try:
    data = serializer.data
    print("Success! No error.")
except Exception as e:
    traceback.print_exc()
