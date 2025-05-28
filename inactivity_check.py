import json
from datetime import datetime
from dateutil.parser import isoparse  # pip install python-dateutil

# JSON 파일 로드
with open('content/spinoff.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

inactive_users = []

for user, entries in data['test'].items():
    if not entries:
        continue

    reference_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)  # 날짜 단위 비교

    diary_dates = []
    for date_key, entry in entries.items():
        try:
            diary_date = datetime.strptime(entry['date'], '%Y-%m-%d %H:%M:%S')
            diary_dates.append(diary_date)
        except Exception as e:
            print(f"날짜 파싱 오류 ({user}): {e}")

    if diary_dates:
        last_diary_date = max(diary_dates).replace(hour=0, minute=0, second=0, microsecond=0)  # 날짜 단위 비교
        time_diff = reference_date - last_diary_date

        if time_diff.days >= 2:
            inactive_users.append(user)

print("2일째 비활성 사용자:", inactive_users)
