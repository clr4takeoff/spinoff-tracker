from flask import Flask, render_template_string
import json
from datetime import datetime
from ready import get_ready_user_info  # 추가된 import

app = Flask(__name__)

@app.route('/')
def show_info():
    with open('content/spinoff.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    inactive_users = []

    for user, entries in data['test'].items():
        if not entries:
            continue

        reference_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
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
                inactive_users.append(user)

    ready_info = get_ready_user_info()

    html = '''
    <h1>Inactive Users (2+ days)</h1>
    <ul>
    {% for user in inactive_users %}
        <li>{{ user }}</li>
    {% endfor %}
    </ul>

    <h2>✅ 공통 이름 (이름-실험자명)</h2>
    <ul>
    {% for name in ready_info.common %}
        <li>{{ name }}</li>
    {% endfor %}
    </ul>

    <h2>📋 설문 응답만 한 사람</h2>
    <ul>
    {% for name in ready_info.only_survey %}
        <li>{{ name }}</li>
    {% endfor %}
    </ul>

    <h2>📮 메일 발송 완료자 중 설문 미응답자</h2>
    <ul>
    {% for name in ready_info.only_application %}
        <li>{{ name }}</li>
    {% endfor %}
    </ul>
    '''
    return render_template_string(html, inactive_users=inactive_users, ready_info=ready_info)

if __name__ == '__main__':
    app.run(debug=True)
