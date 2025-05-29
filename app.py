from flask import Flask, render_template
import json
from datetime import datetime
from ready import get_ready_user_info

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

    ready_info = get_ready_user_info()  # 반환값은 각 카테고리마다 [{"name": ..., "phone": ...}] 형태여야 함

    return render_template('dashboard.html', inactive_users=inactive_users, ready_info=ready_info)

if __name__ == '__main__':
    app.run(debug=True)
