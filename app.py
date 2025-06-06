from flask import Flask, render_template
import json
from datetime import datetime
from ready import get_ready_user_info

app = Flask(__name__)

@app.route('/')
def show_info():
    with open('content/spinoff.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    ready_info = get_ready_user_info()

    # 이름 -> 전화번호 맵 생성
    name_to_phone = {
        item['name'].split('-')[0]: item['phone']
        for item in ready_info['common'] + ready_info['only_application'] + ready_info['only_test']
    }

    # 사용자 ID -> 이름 맵 생성 (userId로 끝나는 사람 찾기)
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
            time_diff = reference_date - last_diary_date

            if time_diff.days >= 2:
                name = user_id_to_name.get(user, user)  # ID에 해당하는 이름이 없으면 ID 그대로 사용
                phone = name_to_phone.get(name, "")
                inactive_users.append({
                    "name": f"{name}-{user}",
                    "phone": phone
                })

    return render_template('dashboard.html', inactive_users=inactive_users, ready_info=ready_info)

if __name__ == '__main__':
    app.run(debug=True)
