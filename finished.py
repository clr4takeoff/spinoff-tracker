# finished.py
import pandas as pd

def get_finished_users(csv_path="content/spinoff 참가 신청서(응답).csv"):
    df = pd.read_csv(csv_path)

    # 필터: 실험 종료된 참가자
    finished_df = df[df['실험 종료 여부'] == 'O']

    users = []
    for _, row in finished_df.iterrows():
        users.append({
            'name': row['성함'],
            'phone': str(row['전화번호 (e.g. 010-0000-0000)']).replace('-', ''),
            'pid': row.get('실험자명', '').strip()  # PID (e.g. P2)
        })

    return users