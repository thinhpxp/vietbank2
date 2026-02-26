import os
import django
import sys
import io
import zipfile

# Setup Django
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ContractDraftingWebApp.settings')
django.setup()

from document_automation.models import LoanProfile, DocumentTemplate, User
from document_automation.views import LoanProfileViewSet
from django.test import RequestFactory

def test_consolidated_export():
    profile = LoanProfile.objects.first()
    if not profile:
        print("Error: No LoanProfile found in database.")
        return

    templates = DocumentTemplate.objects.all()[:2]
    if len(templates) < 1:
        print("Error: Need at least one template.")
        return

    template_ids = [t.id for t in templates]
    batch_template_ids = [templates[0].id] if templates[0].loop_object_type else []

    print(f"Testing Profile: {profile.name} (ID: {profile.id})")
    print(f"Templates: {template_ids}")
    print(f"Batch Template IDs: {batch_template_ids}")

    factory = RequestFactory()
    data = {
        'template_ids': template_ids,
        'batch_template_ids': batch_template_ids,
        'export_mode': 'SINGLE'
    }
    
    request = factory.post(f'/api/loan-profiles/{profile.id}/generate-document/', data, content_type='application/json')
    
    admin = User.objects.filter(is_superuser=True).first()
    request.user = admin

    # Wrap in DRF Request
    from rest_framework.request import Request
    from rest_framework.parsers import JSONParser
    drf_request = Request(request, parsers=[JSONParser()])
    drf_request.user = admin

    view = LoanProfileViewSet()
    view.request = drf_request
    view.format_kwarg = None
    view.kwargs = {'pk': profile.id}
    
    response = view.generate_document(drf_request, profile.id)

    if hasattr(response, 'status_code') and response.status_code != 200:
        print(f"FAIL: Status {response.status_code}")
        if hasattr(response, 'data'): print(response.data)
        return

    content_type = response.get('Content-Type', '')
    print(f"Response Content-Type: {content_type}")

    if 'zip' in content_type:
        zip_data = b"".join(response.streaming_content)
        with zipfile.ZipFile(io.BytesIO(zip_data)) as z:
            file_list = z.namelist()
            print(f"PASS: Received ZIP with {len(file_list)} files:")
            for f in file_list:
                print(f" - {f}")
    elif 'word' in content_type:
        print("PASS: Received individual DOCX (expected if only 1 file generated)")
    else:
        print(f"FAIL: Unexpected Content-Type: {content_type}")

if __name__ == "__main__":
    test_consolidated_export()
