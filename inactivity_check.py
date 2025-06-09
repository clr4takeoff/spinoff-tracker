# inactivity_check.py
import json
from datetime import datetime
from ready import get_ready_user_info

def get_inactive_users():
    with open('content/spinoff.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    ready_info = get_ready_user_info()

    name_to_phone = {
        item['name'].split('-')[0]: item['phone']
        for item in ready_info['common'] + ready_info['only_application'] + ready_info['only_test']
    }

    user_id_to_name = {
        item['name'].split('-')[1]: item['name'].split('-')[0]
        for item in ready_info['common'] + ready_info['only_test']
        if '-' in item['name']
    }

    inactive_users = []
    reference_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    for user, entries in data['test'].items():
        if not entries:
            continue

        diary_dates = []
        for entry in entries.values():
            try:
                diary_date = datetime.strptime(entry['date'], '%Y-%m-%d %H:%M:%S')
                diary_dates.append(diary_date)
            except Exception:
                continue

        if diary_dates:
            last_diary_date = max(diary_dates).replace(hour=0, minute=0, second=0, microsecond=0)
            days_inactive = (reference_date - last_diary_date).days

            if days_inactive >= 2:
                name = user_id_to_name.get(user, user)
                phone = name_to_phone.get(name, "")
                inactive_users.append({
                    "name": f"{name}-{user} (비활성 {days_inactive}일)",
                    "phone": phone
                })

    return ready_info, inactive_users
