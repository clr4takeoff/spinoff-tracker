from flask import Flask, render_template
from inactivity_check import get_inactive_users
from finished import get_finished_users

app = Flask(__name__)

@app.route('/')
def show_dashboard():
    ready_info, inactive_users = get_inactive_users()
    finished_users = get_finished_users()

    return render_template(
        'dashboard.html',
        ready_info=ready_info,
        inactive_users=inactive_users,
        finished_users=finished_users
    )

if __name__ == '__main__':
    app.run(debug=True)
