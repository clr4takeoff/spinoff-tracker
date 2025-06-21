from flask import Flask, render_template
import pandas as pd
import json
from datetime import datetime, timedelta
from collections import defaultdict

app = Flask(__name__)

@app.route("/result")
def show_result():
    # 파일 경로
    json_path = "content/spinoff.json"
    csv_path = "content/spinoff 참가 신청서(응답).csv"

    # JSON 로딩
    with open(json_path, "r", encoding="utf-8") as f:
        json_data = json.load(f)

    # 최초 로그 기준 a/b 계산
    user_dates = {}
    for user, logs in json_data["test"].items():
        if logs:
            log_dates = [datetime.strptime(entry, "%Y-%m-%d %H:%M:%S") for entry in logs.keys()]
            if log_dates:
                first_log = min(log_dates)
                a_date = first_log + timedelta(days=1)
                b_date = a_date + timedelta(days=28)
                user_dates[user] = {"a": a_date.strftime("%Y-%m-%d"), "b": b_date.strftime("%Y-%m-%d")}

    # CSV 불러오기 및 user_id 매핑
    csv_df = pd.read_csv(csv_path)

    def extract_user_id(name):
        if isinstance(name, str) and name.startswith("P") and name[1:].isdigit():
            return name
        return None

    csv_df["user_id"] = csv_df["실험자명"].apply(extract_user_id)

    # 결과 결합
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

    # 그룹화: (a, b) 기준
    grouped_results = defaultdict(lambda: {"rows": [], "all_phones": set()})
    for row in results:
        key = (row["a"], row["b"])
        grouped_results[key]["rows"].append(row)
        grouped_results[key]["all_phones"].update(row["phones"].split(", "))

    # 딕셔너리 정렬 (선택사항)
    grouped_results = dict(sorted(grouped_results.items()))

    return render_template("result.html", grouped_results=grouped_results)

if __name__ == "__main__":
    app.run(debug=True, port=4567)
