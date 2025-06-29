from flask import Flask, render_template
from inactivity_check import get_inactive_users
from finished import get_finished_users, get_sent_phone_numbers, mark_sent_status
import json
app = Flask(__name__)

@app.route('/')
def show_dashboard():
    with open("content/spinoff.json", "r", encoding="utf-8") as f:
        test_logs = json.load(f)["test"]

    ready_info, inactive_users = get_inactive_users()
    finished_users = get_finished_users(test_logs)

    sent_numbers = get_sent_phone_numbers()
    finished_users = mark_sent_status(finished_users, sent_numbers)

    return render_template(
        'dashboard.html',
        ready_info=ready_info,
        inactive_users=inactive_users,
        finished_users=finished_users
    )

if __name__ == '__main__':
    app.run(debug=True)
