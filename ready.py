import pandas as pd
import json

def get_ready_user_info():
    # 파일 경로
    survey_path = 'content/실험 전 설문(응답).csv'
    application_path = 'content/spinoff 참가 신청서(응답).csv'
    json_path = 'content/spinoff.json'

    # 파일 로딩
    df_survey = pd.read_csv(survey_path)
    df_application = pd.read_csv(application_path)

    with open(json_path, 'r', encoding='utf-8') as f:
        spinoff_data = json.load(f)

    test_user_ids = set(user_id.upper() for user_id in spinoff_data['test'].keys())

    # 이름 정리
    df_survey["성함"] = df_survey["성함"].astype(str).str.strip()
    df_application["성함"] = df_application["성함"].astype(str).str.strip()

    # 전체 신청서 기반 이름 → 실험자명 매핑
    full_name_to_experimenter = dict(zip(df_application["성함"], df_application["실험자명"]))
    full_experimenter_to_name = {
        str(v).upper(): k for k, v in full_name_to_experimenter.items() if pd.notna(v)
    }

    # 메일 발송 완료자 필터링
    df_application_filtered = df_application[df_application["실험 안내 메일 발송 여부"] == 'O'].copy()
    name_to_experimenter = dict(zip(df_application_filtered["성함"], df_application_filtered["실험자명"]))

    names_survey = set(df_survey["성함"].dropna())
    names_application = set(name_to_experimenter.keys())

    # 설문자 이름 → 실험자명으로 변환
    experimenters_in_survey = set()
    for name in names_survey:
        if name in full_name_to_experimenter and pd.notna(full_name_to_experimenter[name]):
            experimenters_in_survey.add(str(full_name_to_experimenter[name]).upper())

    # 분류
    common_names = names_survey & names_application
    only_survey = names_survey - names_application
    only_application = names_application - names_survey

    # 공통
    common_name_items = [(name, name_to_experimenter.get(name)) for name in common_names]
    common_name_items.sort(key=lambda x: x[1])
    common_mapped = [f"{name}-{exp}" for name, exp in common_name_items]

    # 신청만 한 사람
    only_application_items = [(name, name_to_experimenter.get(name)) for name in only_application]
    only_application_items.sort(key=lambda x: x[1])
    only_application_mapped = [f"{name}-{exp}" for name, exp in only_application_items]

    # 설문 응답만 한 사람 (테스트 안한 사람만)
    filtered_only_survey = sorted(name for name in only_survey if name != "ㅇ")
    only_survey_final = []
    for name in filtered_only_survey:
        experimenter_id = name_to_experimenter.get(name)
        if not experimenter_id or experimenter_id.upper() not in test_user_ids:
            only_survey_final.append(f"{name}-설문응답")

    # 테스트만 했지만 설문에 없는 사람만 필터링
    test_only_ids = sorted(
        user_id for user_id in test_user_ids
        if user_id not in experimenters_in_survey
    )

    test_only_mapped = []
    for exp_id in test_only_ids:
        name = full_experimenter_to_name.get(exp_id)
        if name:
            test_only_mapped.append(f"{name}-{exp_id}")
        else:
            test_only_mapped.append(f"(이름 없음)-{exp_id}")

    return {
        "common": common_mapped,
        "only_survey": only_survey_final,
        "only_application": only_application_mapped,
        "only_test": test_only_mapped,
    }

# 결과 출력 테스트
if __name__ == "__main__":
    info = get_ready_user_info()

    print("공통 이름 (이름-실험자명):")
    print("\n".join(info['common']) or "해당하는 실험자가 없습니다")

    print("\n설문 응답만 한 사람:")
    print("\n".join(info['only_survey']) or "해당하는 실험자가 없습니다")

    print("\n메일 발송 완료자 중 설문 미응답자:")
    print("\n".join(info['only_application']) or "해당하는 실험자가 없습니다")

    print("\n테스트만 한 사람:")
    print("\n".join(info['only_test']) or "해당하는 실험자가 없습니다")
