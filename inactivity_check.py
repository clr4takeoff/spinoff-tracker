import json
from datetime import datetime
from ready import get_ready_user_info
from finished import get_finished_users

def get_inactive_users():
    with open('content/spinoff.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    test_logs = data["test"]
    ready_info = get_ready_user_info()
    finished_users = get_finished_users(test_logs)

    # 종료된 이름 set
    finished_names = {user['name'] for user in finished_users}
    finished_ids = {user['pid'] for user in finished_users if 'pid' in user}

    # 실험 종료자 제거
    for key in ['common', 'only_application', 'only_test']:
        if key in ready_info:
            ready_info[key] = [
                user for user in ready_info[key]
                if user['name'].split('-')[0] not in finished_names
            ]

    # 전화번호 매핑용 dict
    name_to_phone = {
        item['name'].split('-')[0]: item['phone']
        for key in ['common', 'only_application', 'only_test']
        for item in ready_info.get(key, [])
    }

    # 사용자 ID → 이름 매핑 dict
    user_id_to_name = {
        item['name'].split('-')[1]: item['name'].split('-')[0]
        for key in ['common', 'only_application', 'only_test']
        for item in ready_info.get(key, [])
        if '-' in item['name']
    }

    inactive_users = []
    reference_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    for user, entries in data['test'].items():
        if not entries:
            continue

        # 실험 종료자는 스킵
        if user in finished_ids:
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
