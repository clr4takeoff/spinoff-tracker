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

    # 전화번호 컬럼 자동 감지
    phone_col_candidates = [
        "전화번호", "연락처", "휴대폰", "Phone Number",
        "전화", "핸드폰", "전화번호 (e.g. 010-0000-0000)"
    ]
    phone_col = next((col for col in phone_col_candidates if col in df_application.columns), None)

    if not phone_col:
        raise ValueError(f"전화번호 컬럼이 없습니다. 현재 컬럼들: {df_application.columns.tolist()}")


    # 이름 → 실험자명, 전화번호 매핑
    name_to_exp = dict(zip(df_application["성함"], df_application["실험자명"]))
    name_to_phone = dict(zip(df_application["성함"], df_application[phone_col]))

    full_exp_to_name = {
        str(v).upper(): k for k, v in name_to_exp.items() if pd.notna(v)
    }

    # 필터링
    df_application_filtered = df_application[df_application["실험 안내 메일 발송 여부"] == 'O'].copy()
    filtered_name_to_exp = dict(zip(df_application_filtered["성함"], df_application_filtered["실험자명"]))

    names_survey = set(df_survey["성함"].dropna())
    names_application = set(filtered_name_to_exp.keys())

    experimenters_in_survey = set()
    for name in names_survey:
        if name in name_to_exp and pd.notna(name_to_exp[name]):
            experimenters_in_survey.add(str(name_to_exp[name]).upper())

    # 공통
    common_names = names_survey & names_application
    common_items = []
    for name in sorted(common_names):
        exp = filtered_name_to_exp.get(name)
        phone = name_to_phone.get(name, "")
        display_name = f"{name}-{exp}"
        common_items.append({"name": display_name, "phone": phone})

    # 설문만 한 사람
    only_survey = names_survey - names_application
    only_survey_final = []

    for name in sorted(name for name in only_survey if name and name != "ㅇ" and not any(c.isdigit() for c in name)):
        exp = name_to_exp.get(name)
        if not exp or exp.upper() not in test_user_ids:
            phone = name_to_phone.get(name, "")
            display_name = f"{name}-설문응답"
            only_survey_final.append({"name": display_name, "phone": phone})


    # 신청만 한 사람
    only_application = names_application - names_survey - experimenters_in_test
    only_app_items = []
    for name in sorted(only_application):
        exp = filtered_name_to_exp.get(name)
        phone = name_to_phone.get(name, "")
        display_name = f"{name}-{exp}"
        only_app_items.append({"name": display_name, "phone": phone})

    # 테스트만 한 사람
    test_only_ids = sorted(
        user_id for user_id in test_user_ids
        if user_id not in experimenters_in_survey
    )

    # 테스트한 사람 이름 추출
    experimenters_in_test = {
        name for name, exp in filtered_name_to_exp.items()
        if str(exp).upper() in test_user_ids
    }

    test_items = []
    for exp_id in test_only_ids:
        name = full_exp_to_name.get(exp_id, "(이름 없음)")
        phone = name_to_phone.get(name, "")
        display_name = f"{name}-{exp_id}"
        test_items.append({"name": display_name, "phone": phone})

    return {
        "common": common_items,
        "only_survey": only_survey_final,
        "only_application": only_app_items,
        "only_test": test_items
    }
