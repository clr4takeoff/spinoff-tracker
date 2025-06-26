from flask import Flask, render_template
import pandas as pd
import json
from datetime import datetime, timedelta
from collections import defaultdict

app = Flask(__name__)

def make_sms(a, b):
    return f"""안녕하세요, 최소연 연구자입니다.

‘매 순간의 사건과 기분 대처를 위한 글 작성 연구’ 관련하여, 중간 점검 차 실험 시작 일자와 종료일자를 다시 안내드립니다.

📌 실험 시작일: {a}
📌 실험 종료일: {b}

- 실험 시작일은 테스트 시작일 다음날이며, 종료일은 시작일로부터 28일 후입니다.
- 테스트 시작일에 따라 메일로 안내드린 초기 실험 시작/종료일과 다를 수 있습니다.
- 실험 종료 후 인터뷰를 위한 안내 문자를 보내드릴 예정입니다. 
- 일정이 상이하거나 문의사항이 있을 경우, 본 번호로 연락 주세요.

감사합니다."""

@app.route("/result")
def show_result():
    json_path = "content/spinoff.json"
    csv_path = "content/spinoff 참가 신청서(응답).csv"

    with open(json_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    user_dates = {}
    for user, logs in json_data["test"].items():
        if logs:
            log_dates = [datetime.strptime(entry, "%Y-%m-%d %H:%M:%S") for entry in logs.keys()]
            if log_dates:
                first_log = min(log_dates)
                a_date = first_log + timedelta(days=1)
                b_date = a_date + timedelta(days=28)
                user_dates[user] = {"a": a_date.strftime("%Y-%m-%d"), "b": b_date.strftime("%Y-%m-%d")}

    csv_df = pd.read_csv(csv_path)

    def extract_user_id(name):
        if isinstance(name, str) and name.startswith("P") and name[1:].isdigit():
            return name
        return None

    csv_df["user_id"] = csv_df["실험자명"].apply(extract_user_id)

    results = []
    for user_id, dates in user_dates.items():
        matched_rows = csv_df[csv_df["user_id"] == user_id]
        if not matched_rows.empty:
            phone_numbers = matched_rows["전화번호 (e.g. 010-0000-0000)"].unique()
            results.append({
                "user_id": user_id,
                "a": dates["a"],
                "b": dates["b"],
                "phones": ", ".join(phone_numbers)
            })

    grouped_results = defaultdict(lambda: {"rows": [], "all_phones": set()})
    for row in results:
        key = (row["a"], row["b"])
        grouped_results[key]["rows"].append(row)
        grouped_results[key]["all_phones"].update(row["phones"].split(", "))

    grouped_results = dict(sorted(grouped_results.items()))

    # ✅ 그룹 요약 정보 + 그룹명(A, B, C...) 추가
    group_summaries = []
    labeled_grouped_results = {}  # 그룹명 키로 저장
    for idx, ((a, b), group) in enumerate(grouped_results.items()):
        label = f"Group {chr(65 + idx)}"
        group_summaries.append({
            "label": label,
            "a": a,
            "b": b,
            "count": len(group["rows"])
        })
        labeled_grouped_results[label] = {
            "a": a,
            "b": b,
            "rows": group["rows"],
            "all_phones": group["all_phones"]
        }
        

    return render_template(
        "result.html",
        grouped_results=labeled_grouped_results,
        group_summaries=group_summaries,
        make_sms=make_sms
    )

if __name__ == "__main__":
    app.run(debug=True, port=4567)
