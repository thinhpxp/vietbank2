import requests
import json
import time

def test_api():
    # 1. Login to get token
    print("1. Logging in as admin...")
    login_url = "http://localhost:8000/api/token/"
    login_data = {
        "username": "admin",
        "password": "Admin@123456"
    }
    try:
        res = requests.post(login_url, json=login_data)
        if res.status_code == 200:
            token = res.json().get('access')
            headers = {"Authorization": f"Bearer {token}"}
            print("Login successful.")
        else:
            print(f"Login failed: {res.text}")
            return
            
        # 2. Update a Master Object
        print("2. Fetching existing Master Object...")
        m_res = requests.get("http://localhost:8000/api/master-objects/", headers=headers)
        if m_res.status_code == 200:
            data = m_res.json()
            results = data.get('results', data) if isinstance(data, dict) else data
            if results and isinstance(results, list):
                target = results[0]
                obj_id = target['id']
                print(f"Update MasterObject ID: {obj_id}")
            
            update_data = target
            old_field_values = target.get('field_values', {})
            
            import random
            random_val = f"TEST_NEW_{random.randint(1000, 9999)}"
            
            # Find a field that is currently empty
            # But we don't know the schema easily, let's just use a common one typically empty or create a fake key
            target_key = 'ghi_chu'
            old_val = old_field_values.get(target_key, '')
            update_data['field_values'][target_key] = random_val
            print(f"Changing {target_key}: '{old_val}' -> '{random_val}'")
            
            # API Update
            up_res = requests.patch(f"http://localhost:8000/api/master-objects/{obj_id}/", json={'field_values': update_data['field_values']}, headers=headers)
            print(f"Update response: {up_res.status_code}")
            
            time.sleep(1) # wait for log
            
            # Check Audit Log
            log_res = requests.get(f"http://localhost:8000/api/audit-logs/?target_model=MasterObject:{target['object_type']}&target_id={obj_id}", headers=headers)
            if log_res.status_code == 200 and log_res.json()['results']:
                print(f"Latest Log: {log_res.json()['results'][0]['details']}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_api()
