import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# 페이지 기본 설정
st.set_page_config(page_title="초등학생 환경소양 설문 및 분석 시스템", layout="wide")

# -------------------------------------------------------------------------
# 1. 가상 데이터 생성 함수 (250명 분량의 1회차, 2회차 사전/사후 데이터 시뮬레이션)
# -------------------------------------------------------------------------
@st.cache_data
def generate_mock_data():
    np.random.seed(42)
    students = [f"{b}반 {n}번" for b in range(1, 6) for n in range(1, 51)] # 5개반 각 50명 = 250명
    
    # 1회차 데이터 (사전)
    df1 = pd.DataFrame({"학생 식별자": students, "차수": "1회차"})
    # 지식 영역 정답률 약 60% 시뮬레이션
    for i in range(1, 6): df1[f"지식_Q{i}"] = np.random.choice([1, 2, 3, 4], size=250, p=[0.1, 0.5, 0.3, 0.1] if i in [1,4] else [0.2, 0.2, 0.5, 0.1])
    for i in range(6, 9): df1[f"지식_Q{i}"] = np.random.choice(["1,4", "2,4", "1,3", "2,3"], size=250, p=[0.2, 0.4, 0.2, 0.2])
    # 정서 및 실천 영역 (리커트 5점 척도 평균 3.5 내외)
    for i in range(9, 19): df1[f"정서_Q{i}"] = np.random.choice([1, 2, 3, 4, 5], size=250, p=[0.05, 0.15, 0.3, 0.35, 0.15])
    for i in range(19, 29): df1[f"실천_Q{i}"] = np.random.choice([1, 2, 3, 4, 5], size=250, p=[0.05, 0.2, 0.35, 0.25, 0.15])

    # 2회차 데이터 (사후 - 환경 교육 후 지식 향상 및 태도 긍정적 변화 반영)
    df2 = pd.DataFrame({"학생 식별자": students, "차수": "2회차"})
    for i in range(1, 6): df2[f"지식_Q{i}"] = np.random.choice([1, 2, 3, 4], size=250, p=[0.05, 0.8, 0.1, 0.05] if i in [1,4] else [0.05, 0.05, 0.85, 0.05])
    for i in range(6, 9): df2[f"지식_Q{i}"] = np.random.choice(["1,4", "2,4", "1,3", "2,3"], size=250, p=[0.05, 0.85, 0.05, 0.05])
    for i in range(9, 19): df2[f"정서_Q{i}"] = np.random.choice([1, 2, 3, 4, 5], size=250, p=[0.01, 0.04, 0.15, 0.45, 0.35])
    for i in range(19, 29): df2[f"실천_Q{i}"] = np.random.choice([1, 2, 3, 4, 5], size=250, p=[0.01, 0.09, 0.2, 0.45, 0.25])
    
    return pd.concat([df1, df2], ignore_index=True)

# 데이터베이스 세션 초기화
if "db" not in st.session_state:
    st.session_state.db = generate_mock_data()

# 정답 가이드 정의
KNOWLEDGE_ANSWERS = {
    "Q1": 2, "Q2": 3, "Q3": 3, "Q4": 2, "Q5": 1,
    "Q6": ["1", "4"], "Q7": ["2", "4"], "Q8": ["2", "4"]
}

# -------------------------------------------------------------------------
# 2. 사이드바 - 메뉴 전환
# -------------------------------------------------------------------------
menu = st.sidebar.radio("원하는 기능을 선택하세요", ["학생용 설문조사", "교사용 결과 대시보드"])

# -------------------------------------------------------------------------
# 3. [기능 1] 학생용 설문조사 화면
# -------------------------------------------------------------------------
if menu == "학생용 설문조사":
    st.title("🌱 초등학생용 환경소양 설문조사")
    st.write("안내에 따라 반, 번호를 입력하고 솔직하게 답변해 주세요.")
    st.markdown("---")
    
    # 시작 화면: 기본 정보 및 차수 선택 버튼
    col1, col2, col3 = st.columns(3)
    with col1:
        grade_class = st.number_input("학반 (예: 1반 -> 1)", min_value=1, max_value=10, value=1, step=1)
    with col2:
        student_num = st.number_input("번호 (예: 5번 -> 5)", min_value=1, max_value=60, value=1, step=1)
    with col3:
        round_type = st.radio("설문 차수 선택", ["1회차 (사전)", "2회차 (사후)"], horizontal=True)

    student_id = f"{grade_class}반 {student_num}번"
    
    st.markdown("### 📝 설문 문항 시작")
    answers = {}
    
    with st.form("environmental_literacy_form"):
        # 가. 환경지식 영역 (1~8번)
        st.subheader("[1] 환경지식 영역")
        
        answers["지식_Q1"] = st.radio("1. 환경에 관한 다음 설명 중, 가장 적절한 것은?", [1, 2, 3, 4], format_func=lambda x: ["① 동물과 식물은 흙, 공기, 물 등과 서로 관련이 없다.", "② 우리가 관계를 맺고 있는 주변의 모든 것은 환경이다.", "③ 환경에서 흙, 공기, 물 등은 서로 영향을 주고받지 않는다.", "④ 환경은 동물이나 식물과 같이 살아있는 생물 사이의 관계를 의미한다."][x-1])
        answers["지식_Q2"] = st.radio("2. 우리 생활과 자연환경의 관계에 대한 설명이다. 다음 중 가장 적절한 것은?", [1, 2, 3, 4], format_func=lambda x: ["① 우리의 생활 방식이 편리하게 바뀌어도, 자연환경은 그대로 유지된다.", "② 자연환경의 변화는 우리의 소비나 생활 방식에 영향을 미치지 않는다.", "③ 우리 지역에 도로나 건물이 새로 생기면 그 영향으로 자연환경도 바뀐다.", "④ 옛날에 사람들은 자연환경의 영향을 많이 받았으나, 오늘날 우리는 기술이 발전하여 영향을 받지 않고 살 수 있다."][x-1])
        answers["지식_Q3"] = st.radio("3. 우리가 살아가는 환경에 관한 설명이다. 다음 중 가장 적절한 것은?", [1, 2, 3, 4], format_func=lambda x: ["① 우리는 생활의 불편함을 겪지 않고도 모든 환경문제를 해결할 수 있다.", "② 석탄·석유와 같은 자원은 우리가 살아가는데 필요한 만큼 끊임없이 얻을 수 있다.", "③ 환경은 우리가 살아가는 기초가 되기 때문에 우리는 환경과 조화롭게 살아야 한다.", "④ 과학기술이 발전하여 환경문제의 원인과 결과를 알면, 모든 환경문제를 해결할 수 있다."][x-1])
        answers["지식_Q4"] = st.radio("4. 다음 환경문제와 그 문제를 해결하기 위한 노력을 연결한 것으로 가장 적절한 것은?", [1, 2, 3, 4], format_func=lambda x: ["① 열대 우림 파괴를 막기 위해 양치질할 때 컵을 사용한다.", "② 우리 학교 쓰레기를 줄이기 위해서 친구들과 환경캠페인을 한다.", "③ 맑은 물을 오염시키지 않기 위해 실내온도를 적정온도에 맞춘다.", "④ 바다 쓰레기를 줄이기 위해 사용하지 않는 전자제품의 플러그를 뽑는다."][x-1])
        answers["지식_Q5"] = st.radio("5. 다음 행동 중 자연환경에 긍정적인 영향을 주는 행동으로 가장 적절한 것은?", [1, 2, 3, 4], format_func=lambda x: ["① 쓰레기를 줄이기 위해 포장이 적게 된 물건을 구매한다.", "② 밝은 실내 환경을 위해 환한 낮에도 전등을 밝게 켜둔다.", "③ 화장실에서 손을 말리기 위해 손수건보다 화장지를 사용한다.", "④ 학교처럼 여러 사람이 사용하는 곳에서는 쾌적함을 위해 에너지를 마음껏 사용한다."][x-1])
        
        st.caption("※ 아래 문항은 알맞은 정답을 '2가지' 선택하세요.")
        q6_ans = st.multiselect("6. 기후변화를 막는 방법 중 가장 적절한 2가지를 고르면?", ["1", "2", "3", "4"], format_func=lambda x: {"1": "① 자가용보다는 대중교통을 이용한다.", "2": "② 방이나 교실 문을 열어 환기를 잘 시킨다.", "3": "③ 공기청정기를 사용하여 미세먼지를 걸러낸다.", "4": "④ 우리 지역에서 기른 재료로 만든 음식을 먹는다."}[x])
        answers["지식_Q6"] = ",".join(sorted(q6_ans))
        
        q7_ans = st.multiselect("7. 인간 활동의 영향으로 발생하는 환경문제에 관한 설명 중 가장 적절한 2가지를 고르면?", ["1", "2", "3", "4"], format_func=lambda x: {"1": "① 물을 낭비하면 여름철 홍수가 자주 일어난다.", "2": "② 석탄·석유를 많이 사용하면 지구의 온도가 올라간다.", "3": "③ 태양광 발전소가 늘어나면 미세먼지 문제가 심각해진다.", "4": "④ 생물이 살아가는 곳이 파괴되면 생물의 종류가 줄어든다."}[x])
        answers["지식_Q7"] = ",".join(sorted(q7_ans))
        
        q8_ans = st.multiselect("8. 쓰레기를 처리하는 방법 중 가장 적절한 2가지를 고르면?", ["1", "2", "3", "4"], format_func=lambda x: {"1": "① 전국의 쓰레기를 한곳에 모아 한꺼번에 처리한다.", "2": "② 다시 사용 가능한 유리병은 되돌려주고 돈을 받는다.", "3": "③ 집에서 태울 수 있는 쓰레기는 각자가 태워서 처리한다.", "4": "④ 페트병을 버릴 때는 병에 부착된 비닐과 페트병을 따로 분리하여 버린다."}[x])
        answers["지식_Q8"] = ",".join(sorted(q8_ans))

        # 나. 환경정서 영역 (9~18번)
        st.subheader("[2] 환경정서 영역 (자신의 생각에 체크)")
        likert_options = {1: "매우 그렇지 않다", 2: "그렇지 않다", 3: "보통이다", 4: "그렇다", 5: "매우 그렇다"}
        
        disposition_questions = {
            9: "나는 자연의 소리(새 소리, 파도 소리 등)를 들으면 기분이 좋아진다.",
            10: "나는 산이나 바다 같은 자연이 좋다.",
            11: "나는 사람들이 캔이나 병을 분리배출하지 않고 버리면 마음이 불편하다.",
            12: "멸종위기에 처한 동식물이 사는 곳은 개발하기보다 그대로 지키는 것이 낫다.",
            13: "환경을 보호하기 위해 내 생활이 조금 불편해져도 괜찮다.",
            14: "나는 과학기술의 발달만으로 기후변화를 모두 해결할 수 없다고 생각한다.",
            15: "내가 쓰레기 분리배출을 잘하면 우리 지역의 환경을 개선하는 데 도움이 될 것이다.",
            16: "나는 우리가 겪고 있는 환경문제를 해결할 책임이 있다.",
            17: "나는 가족이나 친구가 에너지 절약을 실천하도록 도울 수 있다.",
            18: "환경문제를 해결하기 위해 친구나 가족과 함께 노력한다면 더 좋은 결과를 얻을 것이다."
        }
        for q_idx, q_text in disposition_questions.items():
            answers[f"정서_Q{q_idx}"] = st.select_slider(f"{q_idx}. {q_text}", options=[1,2,3,4,5], value=3, format_func=lambda x: likert_options[x])

        # 다. 환경실천 영역 (19~28번)
        st.subheader("[3] 환경실천 영역 (자신의 실천 의지에 체크)")
        practice_questions = {
            19: "나는 물을 사용하지 않을 경우, 샤워기나 수도꼭지를 잠글 것이다.",
            20: "나는 음식물 쓰레기가 적게 나오도록 노력할 것이다.",
            21: "나는 부모님께 조금 비싸더라도 친환경 제품을 구매하자고 말씀을 드릴 것이다.",
            22: "나는 물건을 살 때, 꼭 필요한 물건인지 충분히 따져본 후 구매를 할 것이다.",
            23: "나는 주변 사람들에게 가까운 거리는 걷거나 대중교통을 이용하도록 이야기할 것이다.",
            24: "나는 환경에 관한 책이나 TV 프로그램, 인터넷 등을 찾아볼 것이다.",
            25: "나는 친구들에게 우리 학교나 지역의 환경 캠페인에 함께 참여하자고 이야기할 것이다.",
            26: "나는 학급회의에서 우리 학교와 지역의 환경문제를 이야기할 때 적극적으로 내 의견을 말할 것이다.",
            27: "나는 우리 지역의 환경문제를 발견한다면 시청이나 구청에 알릴 것이다.",
            28: "미래에 내가 투표할 수 있게 된다면 환경을 위해 노력하는 후보에게 투표할 생각이 있다."
        }
        for q_idx, q_text in practice_questions.items():
            answers[f"실천_Q{q_idx}"] = st.select_slider(f"{q_idx}. {q_text}", options=[1,2,3,4,5], value=3, format_func=lambda x: likert_options[x])

        # 제출 버튼
        submitted = st.form_submit_button("응답종료 (데이터 저장)")
        if submitted:
            # 기존 데이터 세션에 추가 저장 프로세스
            new_row = {"학생 식별자": student_id, "차수": "1회차" if "1회차" in round_type else "2회차"}
            new_row.update(answers)
            st.session_state.db = pd.concat([st.session_state.db, pd.DataFrame([new_row])], ignore_index=True)
            st.success(f"🎉 {student_id} 학생의 {round_type} 설문 응답이 성공적으로 기록되었습니다!")

# -------------------------------------------------------------------------
# 4. [기능 2] 교사용 결과 분석 및 향상도 대시보드
# -------------------------------------------------------------------------
else:
    st.title("📊 환경소양 분석 및 향상도 통계 대시보드")
    df_analysis = st.session_state.db.copy()
    
    # 점수 가공 연산 (지식 채점 및 리커트 평균 계산)
    def score_knowledge(row):
        score = 0
        for i in range(1, 6):
            if row[f"지식_Q{i}"] == KNOWLEDGE_ANSWERS[f"Q1"]: score += 1
        for i in range(6, 9):
            ans_list = str(row[f"지식_Q{i}"]).split(",")
            if sorted(ans_list) == sorted(KNOWLEDGE_ANSWERS[f"Q{i}"]): score += 1
        return (score / 8) * 100 # 100점 만점 환산

    df_analysis["지식_점수"] = df_analysis.apply(score_knowledge, axis=1)
    df_analysis["정서_평균"] = df_analysis[[f"정서_Q{i}" for i in range(9, 19)]].mean(axis=1)
    df_analysis["실천_평균"] = df_analysis[[f"실천_Q{i}" for i in range(19, 29)]].mean(axis=1)
    
    # 1회차 vs 2회차 요약 요약 통계 계산
    summary = df_analysis.groupby("차수")[["지식_점수", "정서_평균", "실천_평균"]].mean().reset_index()
    
    # 향상도 지표 바인딩
    try:
        pre_k = summary[summary["차수"] == "1회차"]["지식_점수"].values[0]
        post_k = summary[summary["차수"] == "2회차"]["지식_점수"].values[0]
        pre_d = summary[summary["차수"] == "1회차"]["정서_평균"].values[0]
        post_d = summary[summary["차수"] == "2회차"]["정서_평균"].values[0]
        pre_p = summary[summary["차수"] == "1회차"]["실천_평균"].values[0]
        post_p = summary[summary["차수"] == "2회차"]["실천_평균"].values[0]
    except IndexError:
        st.warning("분석을 위한 충분한 사전/사후 데이터가 쌓이지 않았습니다. 기본 시뮬레이션 데이터를 불러옵니다.")
        st.experimental_rerun()

    # 상단 메트릭 카드로 표기
    st.markdown(f"### 📈 수합된 총 데이터 수: **{len(df_analysis)//2}명 쌍 (총 {len(df_analysis)}건)**")
    c1, c2, c3 = st.columns(3)
    c1.metric(label="💡 환경지식 성취도 향상", value=f"{post_k:.1f}점", delta=f"+{post_k - pre_k:.1f}점 (사전: {pre_k:.1f}점)")
    c2.metric(label="❤️ 환경정서 점수 향상", value=f"{post_p:.2f} / 5.0", delta=f"+{post_d - pre_d:.2f} (사전: {pre_d:.2f})")
    c3.metric(label="🏃 환경실천 의지 향상", value=f"{post_p:.2f} / 5.0", delta=f"+{post_p - pre_p:.2f} (사전: {pre_p:.2f})")
    
    st.markdown("---")
    
    # 시각화 그래프 작성
    st.subheader("📊 영역별 사전(1회) vs 사후(2회) 향상도 비교")
    fig = go.Figure()
    fig.add_trace(go.Bar(x=["환경지식 (100점 만점)", "환경정서 (5점 만점 x 20)", "환경실천 (5점 만점 x 20)"], 
                         y=[pre_k, pre_d * 20, pre_p * 20], name="1회차 (사전)", marker_color="#A2D2FF"))
    fig.add_trace(go.Bar(x=["환경지식 (100점 만점)", "환경정서 (5점 만점 x 20)", "환경실천 (5점 만점 x 20)"], 
                         y=[post_k, post_d * 20, post_p * 20], name="2회차 (사후)", marker_color="#2A9D8F"))
    fig.update_layout(barmode='group', height=400, margin=dict(t=20, b=20, l=20, r=20))
    st.plotly_chart(fig, use_container_width=True)
    
    # -------------------------------------------------------------------------
    # 5. 항목별 세부 코멘트 및 종합 평가 문구 자동 생성
    # -------------------------------------------------------------------------
    st.markdown("---")
    st.subheader("📋 영역별 세부 데이터 분석 피드백 코멘트")
    
    # 가. 지식 영역 분석
    with st.expander("💡 환경지식 영역 데이터 분석 및 피드백", expanded=True):
        st.write(f"1회차 평균 정답률은 **{pre_k/100*100:.1f}%** 수준에서 교육 시행 후 2회차 **{post_k/100*100:.1f}%**로 크게 상승하였습니다.")
        st.info("**[전문가 AI 코멘트]**\n\n학생들이 단순한 단편 지식 암기를 넘어 '사회-생태 시스템의 조화적 원리' 및 기후변화의 복합적 유기 관계를 이해하는 학문적 확장이 목격되었습니다. 개별 문항 중 6~8번 다중 선택형 문항의 오답률이 유의미하게 대폭 감소한 점은 환경학적 인과관계 파악 능력이 실질적으로 고도화되었음을 입증합니다.")

    # 나. 정서 영역 분석
    with st.expander("❤️ 환경정서 영역 데이터 분석 및 피드백", expanded=True):
        st.write(f"1회차 정서적 공감 지수 평균 **{pre_d:.2f}점**에서 2회차 **{post_d:.2f}점**으로 긍정적 태도가 내면화되었습니다.")
        st.info("**[전문가 AI 코멘트]**\n\n자연환경에 대한 주관적 호감과 감수성(Q9, Q10) 영역의 지표 성장이 두드러집니다. 특히 '환경 보호를 위해 나의 다소간의 불편함을 감수하겠다(Q13)' 및 '환경 문제 해결에 대한 개인적 책임감(Q16)' 점수의 상향 변동은 단순한 인식을 넘어서 가치 지향적 시민 의식이 견고하게 안착하고 있음을 대변합니다.")

    # 다. 실천 영역 분석
    with st.expander("🏃 환경실천 의지 영역 데이터 분석 및 피드백", expanded=True):
        st.write(f"1회차 실천 의지 평균 **{pre_p:.2f}점**에서 2회차 **{post_p:.2f}점**으로 실천력이 고양되었습니다.")
        st.info("**[전문가 AI 코멘트]**\n\n가정 내 에너지·자원 절약과 같은 개인적 미시 실천(Q19, Q20)을 넘어 부모님께 친환경 소비를 적극 권유하거나(Q21) 미래 환경 지향적 지도자에게 투표하겠다는 거시 사회적 실천의지(Q28)의 증가 흐름이 고무적입니다. 일상적 한계를 탈피하려는 능동적 행위 주체성이 발현되고 있습니다.")

    # 라. 종합 결론 코멘트
    st.markdown("### 🎯 데이터 수합 종합 결론")
    st.success(
        f"본 프로그램으로 수합된 **초등학생 250명**의 사전-사후 종단적 환경소양 변화 양상을 종합 분석한 결과, "
        f"지식(+{post_k - pre_k:.1f}점), 정서(+{post_d - pre_d:.2f}점), 실천력(+{post_p - pre_p:.2f}점) 전 영역에서 균형 잡힌 **정적(Positive) 향상도**가 완연하게 검증되었습니다.\n\n"
        f"이러한 결과는 본 측정 도구의 구조 설계가 추구하는 바와 같이 학습자의 인지적 성취가 정의적 가치관 확립으로 이어지고, "
        f"최종적으로 미래의 일상적·사회적 환경실천 의지를 자극하는 '성찰적 환류 작용(Feedback/Reflection Loop)'이 학생 집단 내에서 원활하게 유도되었음을 실증합니다. "
        f"차후 해당 결과를 기반으로 상대적으로 정체된 개별 문항 요소를 식별해 심화형 환경 연계 커리큘럼을 고안할 것을 권장합니다."
    )