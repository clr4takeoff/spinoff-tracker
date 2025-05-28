from flask import Flask, render_template_string
import json
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def show_inactive_users():
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

    html = '''
    <h1>Inactive Users (2+ days)</h1>
    <ul>
    {% for user in users %}
        <li>{{ user }}</li>
    {% endfor %}
    </ul>
    '''
    return render_template_string(html, users=inactive_users)

if __name__ == '__main__':
    app.run(debug=True)
