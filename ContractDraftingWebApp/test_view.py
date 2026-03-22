import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ContractDraftingWebApp.settings")
django.setup()

from django.test import Client
from django.contrib.auth.models import User
import traceback

client = Client()
try:
    user = User.objects.get(username="admin")
    client.force_login(user)
    print("Logged in as admin")
    response = client.get('/api/master-objects/search/?q=Hồ')
    print("Status:", response.status_code)
    if response.status_code == 500:
        print("Error Traceback visible in HTML?:")
        import re
        html = response.content.decode('utf-8')
        match = re.search(r'<textarea id="traceback_area".*?>(.*?)</textarea>', html, re.DOTALL)
        if match:
            print(match.group(1))
        else:
            print("No traceback area found. Content snippet:", html[:500])
    elif response.status_code == 200:
        print("Success! Return length:", len(response.json()))
    else:
        print("Content:", response.content)
except Exception as e:
    traceback.print_exc()
