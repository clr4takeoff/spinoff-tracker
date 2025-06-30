# finished.py
import pandas as pd
from collections import defaultdict
from datetime import datetime, timedelta
import re


def get_finished_users(test_logs, csv_path="content/spinoff 참가 신청서(응답).csv"):
    df = pd.read_csv(csv_path)
    today = datetime.today().date()
    finished_users = []

    # test_logs 키를 대문자로 변환
    normalized_test_logs = {k.strip().upper(): v for k, v in test_logs.items()}

    for _, row in df.iterrows():
        pid = str(row.get("실험자명", "") or "").strip().upper()
        if not pid or pid not in normalized_test_logs:
            continue

        logs = normalized_test_logs[pid]
        try:
            log_dates = [datetime.strptime(entry, "%Y-%m-%d %H:%M:%S") for entry in logs]
            first_log = min(log_dates)
            a = first_log + timedelta(days=1)
            b = a + timedelta(days=28)
            if b.date() < today:
                finished_users.append({
                    'name': row['성함'],
                    'phone': str(row['전화번호 (e.g. 010-0000-0000)']).replace('-', ''),
                    'pid': pid
                })
        except:
            continue

    return finished_users


def group_finished_users(finished_users, test_logs):
    grouped = defaultdict(lambda: {"users": [], "phones": set()})
    normalized_test_logs = {k.strip().upper(): v for k, v in test_logs.items()}

    for user in finished_users:
        pid = user.get("pid", "").strip().upper()
        if not pid or pid not in normalized_test_logs:
            continue

        logs = normalized_test_logs.get(pid)
        if logs:
            try:
                log_dates = [datetime.strptime(entry, "%Y-%m-%d %H:%M:%S") for entry in logs.keys()]
                first_log = min(log_dates)
                a = (first_log + timedelta(days=1)).strftime("%Y-%m-%d")
                b = (first_log + timedelta(days=29)).strftime("%Y-%m-%d")
                key = (a, b)
                grouped[key]["users"].append(user)
                grouped[key]["phones"].add(user["phone"])
            except:
                continue

    result = []
    for idx, ((a, b), group) in enumerate(sorted(grouped.items())):
        label = f"Group {chr(65 + idx)}"
        result.append({
            "label": label,
            "a": a,
            "b": b,
            "users": group["users"],
            "phones": ", ".join(group["phones"])
        })
    return result

def get_sent_phone_numbers(path="static/sent_phones.txt"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            # 정규식으로 쉼표 또는 줄바꿈 기준으로 분리
            numbers = re.split(r'[,\n]+', content)
            # 공백 제거 + 빈 문자열 제거
            return set(num.strip() for num in numbers if num.strip())
    except FileNotFoundError:
        return set()


def mark_sent_status(finished_users, sent_numbers):
    for user in finished_users:
        user['is_sent'] = user.get('phone') in sent_numbers
    return finished_users
