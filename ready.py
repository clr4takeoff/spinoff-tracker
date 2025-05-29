import pandas as pd

# 파일 경로
survey_path = 'content/실험 전 설문(응답).csv'
application_path = 'content/spinoff 참가 신청서(응답).csv'

# CSV 로딩
df_survey = pd.read_csv(survey_path)
df_application = pd.read_csv(application_path)

# 설문자 이름 정리
df_survey["성함"] = df_survey["성함"].astype(str).str.strip()
names_survey = set(df_survey["성함"].dropna())

# 메일 발송 완료자 필터링 (복사본으로 원본 보호)
df_application_filtered = df_application[df_application["실험 안내 메일 발송 여부"] == 'O'].copy()
df_application_filtered["성함"] = df_application_filtered["성함"].astype(str).str.strip()

# 이름-실험자명 매핑
name_to_experimenter = dict(zip(df_application_filtered["성함"], df_application_filtered["실험자명"]))
names_application = set(name_to_experimenter.keys())

# 이름 비교
common_names = names_survey & names_application
only_survey = names_survey - names_application
only_application = names_application - names_survey

# 공통 이름 정렬 (실험자명 기준)
common_name_items = [(name, name_to_experimenter.get(name)) for name in common_names]
common_name_items.sort(key=lambda x: x[1])  # 실험자명 기준 정렬
common_mapped = [f"{name}-{exp}" for name, exp in common_name_items]

# 메일 발송 완료자 중 설문 미응답자 정렬 (실험자명 기준)
only_application_items = [(name, name_to_experimenter.get(name)) for name in only_application]
only_application_items.sort(key=lambda x: x[1])
only_application_mapped = [f"{name}-{exp}" for name, exp in only_application_items]

# 설문 응답만 한 사람 정리 (이름 기준 정렬)
filtered_only_survey = sorted(name for name in only_survey if name != "ㅇ")

# 출력
print("공통 이름 (이름-실험자명):")
if common_mapped:
    for mapped in common_mapped:
        print(mapped)
else:
    print("해당하는 실험자가 없습니다")

print("\n설문 응답만 한 사람 (이름-설문응답):")
if filtered_only_survey:
    for name in filtered_only_survey:
        print(f"{name}-설문응답")
else:
    print("해당하는 실험자가 없습니다")

print("\n메일 발송 완료자 중 설문 미응답자 (이름-실험자명):")
if only_application_mapped:
    for mapped in only_application_mapped:
        print(mapped)
else:
    print("해당하는 실험자가 없습니다")


import pandas as pd

def get_ready_user_info():
    survey_path = 'content/실험 전 설문(응답).csv'
    application_path = 'content/spinoff 참가 신청서(응답).csv'

    df_survey = pd.read_csv(survey_path)
    df_application = pd.read_csv(application_path)

    df_survey["성함"] = df_survey["성함"].astype(str).str.strip()
    names_survey = set(df_survey["성함"].dropna())

    df_application_filtered = df_application[df_application["실험 안내 메일 발송 여부"] == 'O'].copy()
    df_application_filtered["성함"] = df_application_filtered["성함"].astype(str).str.strip()

    name_to_experimenter = dict(zip(df_application_filtered["성함"], df_application_filtered["실험자명"]))
    names_application = set(name_to_experimenter.keys())

    common_names = names_survey & names_application
    only_survey = names_survey - names_application
    only_application = names_application - names_survey

    common_name_items = [(name, name_to_experimenter.get(name)) for name in common_names]
    common_name_items.sort(key=lambda x: x[1])
    common_mapped = [f"{name}-{exp}" for name, exp in common_name_items]

    only_application_items = [(name, name_to_experimenter.get(name)) for name in only_application]
    only_application_items.sort(key=lambda x: x[1])
    only_application_mapped = [f"{name}-{exp}" for name, exp in only_application_items]

    filtered_only_survey = sorted(name for name in only_survey if name != "ㅇ")
    filtered_only_survey_mapped = [f"{name}-설문응답" for name in filtered_only_survey]

    return {
        "common": common_mapped,
        "only_survey": filtered_only_survey_mapped,
        "only_application": only_application_mapped,
    }
