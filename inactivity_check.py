import json
from datetime import datetime
from dateutil.parser import isoparse  # pip install python-dateutil
from ready import get_ready_user_info  # ready.py에서 사용자 정보 가져오기

# JSON 파일 로드
with open('content/spinoff.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# ready.py에서 사용자 정보 가져오기
ready_info = get_ready_user_info()
# 이름과 전화번호 매핑 생성 (common, only_application, only_test에서 이름-전화번호 쌍 추출)
name_to_phone = {item['name'].split('-')[0]: item['phone'] for item in ready_info['common'] + ready_info['only_application'] + ready_info['only_test']}

inactive_users = []

# 테스트 데이터의 각 사용자에 대해 비활성 여부 확인
for user, entries in data['test'].items():
    if not entries:
        continue  # 데이터가 없으면 건너뛰기

    # 기준 날짜 설정 (오늘 자정으로 설정하여 날짜 단위 비교)
    reference_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    diary_dates = []
    # 각 엔트리의 날짜 파싱
    for date_key, entry in entries.items():
        try:
            diary_date = datetime.strptime(entry['date'], '%Y-%m-%d %H:%M:%S')
            diary_dates.append(diary_date)
        except Exception as e:
            print(f"날짜 파싱 오류 ({user}): {e}")

    if diary_dates:
        # 가장 최근 날짜를 기준으로 비활성 여부 판단
        last_diary_date = max(diary_dates).replace(hour=0, minute=0, second=0, microsecond=0)
        time_diff = reference_date - last_diary_date

        # 2일 이상 활동이 없으면 비활성 사용자로 추가: 검색 날짜 제외
        if time_diff.days >= 3:
            # 사용자 이름 찾기 (ready_info에서 사용자 ID와 매칭되는 이름 추출)
            name = next((item['name'].split('-')[0] for item in ready_info['common'] + ready_info['only_test'] if item['name'].endswith(user)), user)
            # 전화번호 가져오기 (없으면 빈 문자열)
            phone = name_to_phone.get(name, "")
            # dashboard.html과 호환되도록 이름과 전화번호를 딕셔너리로 추가
            inactive_users.append({"name": f"{name}-{user}", "phone": phone})

# 비활성 사용자 목록 출력
print("2일째 비활성 사용자:", inactive_users)