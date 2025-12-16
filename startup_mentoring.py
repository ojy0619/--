import streamlit as st
from openai import OpenAI
import time
import datetime
import os
from dotenv import load_dotenv

# .env 파일에서 API 키 로드
load_dotenv()

# -------------------------------------------------------------------
# [TPACK - TK] 교육적 환경 구성을 위한 UI/UX 설정
# 기존의 귀여운 느낌보다는 깔끔하고 신뢰감 있는 교실 분위기로 변경
# -------------------------------------------------------------------
st.set_page_config(
    page_title="창업 멘토링 교실",
    page_icon="👩‍🏫",
    layout="centered"
)

# [커스텀 CSS] 집중도를 높이는 깔끔한 디자인
# 폰트: 가독성 좋은 고딕 계열 / 색감: 차분한 네이비 & 화이트
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', sans-serif;
    }
    .stApp {
        background-color: #F0F2F6; /* 차분한 회색조 배경 */
    }
    .chat-bubble {
        padding: 15px;
        border-radius: 10px;
        margin-bottom: 10px;
        box-shadow: 1px 1px 3px rgba(0,0,0,0.1);
    }
    h1 {
        color: #1A237E; /* 신뢰감 있는 네이비 색상 */
        text-align: center;
        font-weight: 700;
    }
    .stButton>button {
        background-color: #3949AB;
        color: white;
        border-radius: 5px;
        font-weight: bold;
    }
    .stInfo {
        background-color: #E8EAF6;
        color: #1A237E;
    }
    </style>
    """, unsafe_allow_html=True)

# -------------------------------------------------------------------
# [TPACK - TK] API 키 보안 설정
# -------------------------------------------------------------------
# Streamlit secrets 또는 .env 파일에서 API 키 로드
if "OPENAI_API_KEY" in st.secrets:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
elif os.getenv("OPENAI_API_KEY"):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
else:
    # 사이드바에서 API 키 입력 받기
    with st.sidebar:
        st.header("⚙️ 설정")
        api_key_input = st.text_input(
            "OpenAI API Key",
            type="password",
            help="OpenAI API 키를 입력하세요. .env 파일에 OPENAI_API_KEY로 설정하거나 여기에 직접 입력하세요.",
            placeholder="API 키를 입력하세요..."
        )
    
    if api_key_input:
        client = OpenAI(api_key=api_key_input)
    else:
        st.error("🚨 선생님이 칠판을 준비하지 못했어요. (API 키를 설정해주세요)")
        st.info("💡 .env 파일에 OPENAI_API_KEY를 설정하거나, 사이드바에서 직접 입력하세요.")
        st.stop()

# -------------------------------------------------------------------
# [TPACK - PK] 스캐폴딩(Scaffolding) & 학습 목표 제시
# -------------------------------------------------------------------
with st.sidebar:
    st.header("👩‍🏫 창업 멘토링실")
    st.info("""
    **학습 목표:**
    1. 생활 속 문제를 해결하는 창의적인 아이디어를 제안한다.
    2. 선생님의 피드백을 반영하여 아이디어의 현실성을 높인다.
    """)
    
    # [설정] 창업 분야 선택
    category = st.selectbox(
        "탐구 주제 선택",
        ["🏫 학교 생활 개선", "🌍 환경 보호", "🤖 미래 기술 활용", "🏠 안전한 우리 집"]
    )
    
    st.divider()
    
    # [과정 중심 평가] 포트폴리오 저장
    if st.button("📝 상담 일지 저장하기"):
        chat_log = ""
        if "messages" in st.session_state:
            for msg in st.session_state.messages:
                role = "선생님" if msg["role"] == "assistant" else "학생"
                if msg["role"] != "system":
                    chat_log += f"[{role}] {msg['content']}\n"
        
        if chat_log:
            st.download_button(
                label="💾 파일로 내려받기",
                data=chat_log,
                file_name=f"창업멘토링_{datetime.datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )
        else:
            st.warning("저장할 대화 내용이 없습니다.")

# -------------------------------------------------------------------
# [TPACK - CK/PK] 페르소나: 카리스마 있는 5년 차 선생님
# -------------------------------------------------------------------
system_prompt = f"""
당신은 친절하지만 카리스마 있는 5년 차 초등학교 선생님입니다.
현재 수업 주제: {category}

[성격 및 말투]
1. 말투: 기본적으로 존댓말을 쓰되, 단호하고 명확하게 말합니다. (예: "그 부분은 다시 생각해볼까요?", "좋습니다.")
2. 태도: 학생을 존중하지만, 만만하게 보이지 않습니다. 엉뚱하거나 성의 없는 답변에는 따끔하게 지적합니다.
3. 이모지: 교육적 강조가 필요할 때가 아니면 거의 사용하지 않습니다.

[지도 방식 (소크라테스식 문답법)]
1. 정답을 바로 주지 않습니다.
2. 학생의 아이디어에서 **'실현 가능성', '예산(가격)', '안전성', '윤리적 문제'** 중 가장 취약한 부분을 찾아 날카롭게 질문하세요.
   (예: "취지는 좋지만, 초등학생이 감당하기엔 제작 비용이 너무 비싸지 않을까요?")
3. 학생이 지적받은 내용을 구체적으로 수정하면, 그때 비로소 "아주 훌륭합니다. 정확하게 문제를 해결했군요."라고 칭찬해주세요.
"""

st.title("👩‍🏫 창업 아이디어 멘토링")
st.write(f"### 주제: **{category}** 프로젝트")
st.markdown("---")

# -------------------------------------------------------------------
# 채팅 인터페이스
# -------------------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": system_prompt}]
    st.session_state.idea_selected = False
    st.session_state.custom_idea = ""

# 대화 기록 시각화
for message in st.session_state.messages:
    if message["role"] != "system":
        # 아바타 변경: 고양이 -> 선생님/학생
        avatar = "👩‍🏫" if message["role"] == "assistant" else "🧒"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"])

# -------------------------------------------------------------------
# [교육적 빌드업] 시작 화면 - 아이디어 선택
# -------------------------------------------------------------------
if not st.session_state.idea_selected and len([m for m in st.session_state.messages if m["role"] != "system"]) == 0:
    st.markdown("""
    <div style='background-color: #E8EAF6; padding: 25px; border-radius: 15px; margin: 20px 0; border-left: 5px solid #3949AB;'>
        <h3 style='color: #1A237E; margin-bottom: 15px;'>안녕하세요! 선생님입니다.</h3>
        <p style='color: #1A237E; font-size: 1.1em; line-height: 1.8;'>
            오늘은 여러분이 직접 생각해낸 아이디어를 현실적인 창업 아이디어로 발전시켜보는 시간입니다.
            <br><br>
            <strong>어떤 물건이나 아이디어를 생각해 내서 팔아보고 싶어요?</strong>
            <br><br>
            아래에서 가장 관심 있는 분야를 선택해주세요. 선택한 내용을 바탕으로 선생님이 여러분의 아이디어를 함께 발전시켜드릴게요.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 💡 아이디어 선택하기")
    
    # 아이디어 선택지
    idea_options = [
        "🎨 만들기/공예 관련 (예: 손수건, 열쇠고리, 스티커 등)",
        "🍪 음식/간식 관련 (예: 쿠키, 젤리, 음료 등)",
        "📚 학습 도구/문구 관련 (예: 노트, 필기구, 스티커북 등)",
        "🎮 게임/놀이 관련 (예: 보드게임, 퍼즐, 장난감 등)",
        "🌱 환경/생활 개선 관련 (예: 재활용품, 생활용품 등)",
        "💻 디지털/기술 관련 (예: 앱, 웹사이트, 프로그램 등)",
        "기타 (직접 입력)"
    ]
    
    selected_option = st.radio(
        "아이디어 유형을 선택하세요:",
        idea_options,
        key="idea_selection"
    )
    
    # 기타 선택 시 직접 입력 받기
    if selected_option == "기타 (직접 입력)":
        custom_input = st.text_input(
            "어떤 종류의 아이디어를 원하시나요?",
            placeholder="예: 운동용품, 반려동물 용품, 패션 아이템 등",
            key="custom_idea_input"
        )
        
        if st.button("선택 완료", type="primary", use_container_width=True, disabled=not custom_input):
            if custom_input:
                user_input = f"저는 {custom_input} 관련 아이디어를 생각해보고 싶어요."
                st.session_state.idea_selected = True
                st.session_state.messages.append({"role": "user", "content": user_input})
                
                # 즉시 AI 응답 생성
                with st.spinner("선생님이 아이디어를 검토하고 있습니다..."):
                    time.sleep(1.2)
                    response = client.chat.completions.create(
                        model="gpt-4o-mini",
                        messages=st.session_state.messages
                    )
                    ai_reply = response.choices[0].message.content
                    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                st.rerun()
    else:
        if st.button("선택 완료", type="primary", use_container_width=True):
            # 선택지에서 이모지와 설명 제거하고 핵심 키워드만 추출
            clean_option = selected_option.split("(")[0].strip()
            user_input = f"저는 {clean_option} 관련 아이디어를 생각해보고 싶어요."
            st.session_state.idea_selected = True
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # 즉시 AI 응답 생성
            with st.spinner("선생님이 아이디어를 검토하고 있습니다..."):
                time.sleep(1.2)
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=st.session_state.messages
                )
                ai_reply = response.choices[0].message.content
                st.session_state.messages.append({"role": "assistant", "content": ai_reply})
            st.rerun()

# -------------------------------------------------------------------
# [TPACK - TK] 실시간 상호작용
# -------------------------------------------------------------------
if st.session_state.idea_selected:
    if user_input := st.chat_input("아이디어를 구체적으로 설명해주세요 (예: 칠판 지우개 청소 로봇)"):
        
        # 1. 학생 입력 표시
        st.chat_message("user", avatar="🧒").markdown(user_input)
        st.session_state.messages.append({"role": "user", "content": user_input})

        # 2. AI 생각 효과 (진지한 검토 느낌)
        with st.spinner("선생님이 아이디어를 검토하고 있습니다..."):
            time.sleep(1.2) 
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=st.session_state.messages
            )
            ai_reply = response.choices[0].message.content

        # 3. AI 답변 표시
        st.chat_message("assistant", avatar="👩‍🏫").markdown(ai_reply)
        st.session_state.messages.append({"role": "assistant", "content": ai_reply})

            # 4. [보상 시스템] 성취감 부여
        # 선생님의 칭찬 키워드가 있을 때만 축하 효과
        positive_keywords = ["훌륭합니다", "정확합니다", "통과", "잘했습니다", "탁월합니다"]
        if any(keyword in ai_reply for keyword in positive_keywords):
            st.balloons()
            st.success("🎉 통과! 아주 논리적인 수정이었습니다. 상담 일지를 저장하세요.")

