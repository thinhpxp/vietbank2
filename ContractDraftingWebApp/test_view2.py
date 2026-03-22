import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ContractDraftingWebApp.settings")
django.setup()

from django.test import RequestFactory
from django.contrib.auth.models import User
from document_automation.views.master_views import MasterObjectViewSet
import traceback

factory = RequestFactory()
request = factory.get('/api/master-objects/search/?q=Hồ')

try:
    user = User.objects.get(username="admin")
    request.user = user
    request.query_params = request.GET
    print("Calling the view directly...")
    view_func = MasterObjectViewSet.as_view({'get': 'search'})
    response = view_func(request)
    # The view might wrap in Response, let's render it
    response.render()
    print("Success. Status =", response.status_code)
except Exception as e:
    with open('error_trace_utf8.txt', 'w', encoding='utf-8') as f:
        traceback.print_exc(file=f)
