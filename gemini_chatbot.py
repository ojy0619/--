import streamlit as st
import requests
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

# [커스텀 CSS] 아기자기하지만 가독성 좋은 디자인
# 파스텔 톤 배경 + 진한 글씨 색상으로 대비 확보
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Noto Sans KR', sans-serif;
        color: #000000;
    }
    
    .stApp {
        background: radial-gradient(circle at top left, #FFE5F0 0%, #FFF8E1 35%, #E3F2FD 100%);
    }

    h1, h2, h3, h4, h5, h6, p, span, label {
        color: #000000 !important;
    }

    /* 메인 영역 카드 느낌 */
    .main > div {
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 16px;
        padding: 24px 20px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08);
    }

    /* 버튼: 파스텔 톤 */
    .stButton>button {
        background: linear-gradient(135deg, #FFB6C1, #FFCC80);
        color: #000000;
        border-radius: 999px;
        font-weight: 700;
        border: none;
        padding: 0.4rem 1.2rem;
    }
    .stButton>button:hover {
        opacity: 0.95;
        box-shadow: 0 4px 10px rgba(255, 182, 193, 0.6);
    }

    /* 정보 박스 */
    .stInfo {
        background-color: #FFF3E0;
        color: #000000;
        border-radius: 12px;
    }

    /* 사이드바 배경 */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #FFF3E0 0%, #F3E5F5 100%);
    }

    /* 채팅 말풍선 느낌 (기본 텍스트 대비 강화용) */
    .stChatMessage p,
    .stChatMessage div,
    .stChatMessage span,
    .stChatMessage * {
        color: #000000 !important;
    }
    
    /* Expander 내부 텍스트 색상 (검정색) */
    [data-testid="stExpander"] p,
    [data-testid="stExpander"] h3,
    [data-testid="stExpander"] h4,
    [data-testid="stExpander"] li,
    [data-testid="stExpander"] strong {
        color: #000000 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# -------------------------------------------------------------------
# [TPACK - TK] API 키 보안 설정 (Google Gemini)
# -------------------------------------------------------------------
# Streamlit secrets 또는 .env 파일에서 Gemini API 키 로드
gemini_api_key: str | None = None

if "GOOGLE_API_KEY" in st.secrets:
    gemini_api_key = st.secrets["GOOGLE_API_KEY"]
elif os.getenv("GOOGLE_API_KEY"):
    gemini_api_key = os.getenv("GOOGLE_API_KEY")
else:
    # 사이드바에서 API 키 입력 받기
    with st.sidebar:
        st.header("⚙️ 설정")
        api_key_input = st.text_input(
            "Google Gemini API Key",
            type="password",
            help="Google AI Studio에서 발급한 Gemini API 키를 입력하세요. .env 파일에 GOOGLE_API_KEY로 설정하거나 여기에 직접 입력할 수 있습니다.",
            placeholder="예: AIxxx..."
        )

    if api_key_input:
        # API 키가 변경되었는지 확인
        if "previous_api_key" not in st.session_state:
            st.session_state.previous_api_key = api_key_input
        elif st.session_state.previous_api_key != api_key_input:
            # API 키가 변경되었으면 세션 상태 완전 초기화
            st.session_state.clear()
            st.session_state.previous_api_key = api_key_input
            st.rerun()
        
        gemini_api_key = api_key_input
    else:
        st.error("🚨 선생님이 칠판을 준비하지 못했어요. (Gemini API 키를 설정해주세요)")
        st.info("💡 .env 파일에 GOOGLE_API_KEY를 설정하거나, 사이드바에서 직접 입력하세요.")
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
# 시스템 프롬프트 템플릿 (category 변수를 사용하기 전에 정의)
system_prompt_template = """
당신은 친절하지만 카리스마 있는 5년 차 초등학교 선생님입니다.
현재 수업 주제: {category}

[성격 및 말투]
1. 말투: 기본적으로 존댓말을 쓰되, 단호하고 명확하게 말합니다. (예: "그 부분은 다시 생각해볼까요?", "좋습니다.")
2. 태도: 학생을 존중하지만, 만만하게 보이지 않습니다. 다만, 어떤 의견이든 먼저 긍정적인 부분을 찾아주고, 그 다음에 보완점을 설명합니다.
3. 이모지: 교육적 강조가 필요할 때가 아니면 거의 사용하지 않습니다.

[다양한 의견 수용 방식]
1. 학생의 아이디어가 비현실적이거나 엉뚱해 보여도 바로 '틀렸다'고 말하지 않습니다.
2. "그 생각도 의미가 있어요. 다만, 이런 점을 조금 더 생각해보면 좋겠어요."처럼, 먼저 이해와 공감을 표현한 뒤에 수정 방향을 제시합니다.
3. 학생이 하고 싶은 말의 의도를 최대한 선하게 해석하고, 판단하거나 비난하기보다 '함께 수정해 나가는 파트너'처럼 대화합니다.

[지도 방식 (소크라테스식 문답법 + 예시 제시)]
1. 정답을 바로 주지 않습니다.
2. 학생의 아이디어에서 '실현 가능성', '예산(가격)', '안전성', '윤리적 문제' 중 취약해 보이는 부분을 골라, 생각을 더 깊이 하게 만드는 질문을 합니다.
   (예: "취지는 좋지만, 초등학생이 감당하기엔 제작 비용이 너무 비싸지 않을까요?")
3. 학생이 지적받은 내용을 구체적으로 수정하면, 그때 비로소 "아주 훌륭합니다. 정확하게 문제를 해결했군요."라고 칭찬해주세요.
4. 여러 방향의 해결책이 있을 수 있음을 인정하고, "이렇게도 할 수 있고, 저렇게도 할 수 있어요."처럼 다양한 선택지를 제시합니다.
5. 학생이 많이 막혀 있거나 아이디어를 내기 어려워하면, 먼저 예시 발명품(창업 아이템)을 하나 제시해서 아래 항목을 함께 짚어 봅니다.
   - 어떤 문제를 해결하려고 만든 발명품인지
   - **어떤 부분들을 고려했는지** (사용자, 장소, 시간, 필요한 재료 등)
   - **어떤 것을 중점으로 생각했는지** (편리함, 안전, 환경 보호, 재미 등)
   - **어떤 주의점이 있는지** (위험 요소, 관리 방법, 규칙 등)
   - **가격은 어느 정도로 예상하는지** (선택 사항이며, 너무 비싸지 않게 조심해야 한다는 점을 알려줍니다.)
   - **어떤 교육적 이점이 있는지** (협동심, 책임감, 창의성, 문제 해결 능력 등)
6. 처음부터 예시를 들 때에도, 예시만 설명하고 끝내지 말고,
   "지금 선생님 예시처럼, 너도 문제·중점·주의점·가격(선택)·교육적 이점을 차근차근 정리해 볼까요?"라고 말하며 학생이 따라 할 수 있도록 도와줍니다.
"""

# 시스템 프롬프트 생성 함수
def get_system_prompt(category: str) -> str:
    """카테고리에 맞는 시스템 프롬프트를 생성합니다."""
    return system_prompt_template.format(category=category)

# 현재 카테고리에 맞는 시스템 프롬프트 생성
system_prompt = get_system_prompt(category)


def call_gemini(messages: list[dict], category: str) -> str:
    """
    현재 대화 내용을 바탕으로 Gemini 2.5 Flash에 요청을 보내고,
    선생님 AI의 응답 텍스트를 반환합니다.
    
    Args:
        messages: 대화 메시지 리스트
        category: 현재 선택된 카테고리
    """
    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        "models/gemini-2.5-flash:generateContent"
        f"?key={gemini_api_key}"
    )

    # Streamlit용 메시지 포맷을 Gemini 포맷으로 변환
    contents: list[dict] = []
    for msg in messages:
        role = msg.get("role")
        if role == "user":
            g_role = "user"
        elif role == "assistant":
            g_role = "model"
        else:
            # system 등은 systemInstruction으로 따로 전달
            continue

        contents.append(
            {
                "role": g_role,
                "parts": [{"text": msg.get("content", "")}],
            }
        )

    # 현재 카테고리에 맞는 시스템 프롬프트 가져오기
    current_system_prompt = get_system_prompt(category)
    
    payload = {
        "contents": contents,
        "systemInstruction": {
            "parts": [{"text": current_system_prompt}],
        },
    }

    # 재시도 로직 (503 오류 대응)
    max_retries = 3
    retry_delay = 2
    
    for attempt in range(max_retries):
        try:
            resp = requests.post(
                url,
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=30,
            )
            
            if resp.status_code == 401:
                raise RuntimeError(
                    "Gemini API 인증 오류입니다. GOOGLE_API_KEY 값을 다시 확인해 주세요."
                )
            
            if resp.status_code == 503:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay * (attempt + 1))
                    continue
                else:
                    raise RuntimeError(
                        "Gemini API 서버가 일시적으로 사용할 수 없습니다. 잠시 후 다시 시도해주세요. (503 Service Unavailable)"
                    )
            
            resp.raise_for_status()
            break
            
        except requests.exceptions.Timeout:
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (attempt + 1))
                continue
            else:
                raise RuntimeError("Gemini API 요청 시간이 초과되었습니다. 네트워크 연결을 확인해주세요.")
        except requests.exceptions.RequestException as e:
            if attempt < max_retries - 1:
                time.sleep(retry_delay * (attempt + 1))
                continue
            else:
                raise RuntimeError(f"Gemini API 통신 오류: {e}")
        except requests.exceptions.HTTPError as e:
            if resp.status_code == 503 and attempt < max_retries - 1:
                time.sleep(retry_delay * (attempt + 1))
                continue
            else:
                raise RuntimeError(f"Gemini API 응답 오류: {e}")

    data = resp.json()
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError) as e:
        raise RuntimeError(f"Gemini 응답 파싱 중 오류가 발생했습니다: {e}") from e

st.title("👩‍🏫 창업 아이디어 멘토링")
st.write(f"### 주제: **{category}** 프로젝트")
st.markdown("---")

# -------------------------------------------------------------------
# 채팅 인터페이스 초기화
# -------------------------------------------------------------------
# 세션 상태 초기화 (처음 실행 시)
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": get_system_prompt(category)}]
    st.session_state.idea_selected = False
    st.session_state.custom_idea = ""

# idea_selected가 없거나 초기화가 필요한 경우 - 확실하게 False로 설정
if "idea_selected" not in st.session_state:
    st.session_state.idea_selected = False

# idea_selected가 True인데 실제로 선택된 메시지가 없으면 다시 False로
if st.session_state.idea_selected:
    user_messages = [m for m in st.session_state.messages if m.get("role") == "user"]
    if len(user_messages) == 0:
        st.session_state.idea_selected = False

# 추가 안전장치: messages에 system만 있으면 idea_selected를 False로
if "messages" in st.session_state:
    non_system_messages = [m for m in st.session_state.messages if m.get("role") != "system"]
    if len(non_system_messages) == 0:
        st.session_state.idea_selected = False

# -------------------------------------------------------------------
# [교육적 빌드업] 시작 화면 - 아이디어 선택
# -------------------------------------------------------------------
# 선택지가 아직 선택되지 않았으면 선택지 화면 표시
if not st.session_state.idea_selected:
    st.markdown("""
    <div style='background-color: #E8EAF6; padding: 25px; border-radius: 15px; margin: 20px 0; border-left: 5px solid #3949AB;'>
        <h3 style='color: #000000; margin-bottom: 15px;'>안녕하세요! 선생님입니다.</h3>
        <p style='color: #000000; font-size: 1.1em; line-height: 1.8;'>
            오늘은 여러분이 직접 생각해낸 아이디어를 현실적인 창업 아이디어로 발전시켜보는 시간입니다.
            <br><br>
            <strong>어떤 물건이나 아이디어를 생각해 내서 팔아보고 싶어요?</strong>
            <br><br>
            아래에서 가장 관심 있는 분야를 선택해주세요. 선택한 내용을 바탕으로 선생님이 여러분의 아이디어를 함께 발전시켜드릴게요.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 💡 아이디어 선택하기")
    st.markdown(
        """
        - **실생활 문제**와 연결되는 주제를 고르면 설득력이 높아요.
        - 가격·안전·환경·윤리 중 무엇을 특히 챙길지 미리 생각해보세요.
        - 팀워크/리더십/창의력/문제해결 같은 **교육적 이점**도 한 줄 넣어보면 좋아요.
        """
    )

    # 아이디어 선택지 (교육적 포인트를 살짝 담은 예시 포함)
    idea_options = [
        "🎨 만들기/공예 (예: 손수건, 업사이클 굿즈) — 손재주·창의력",
        "🍪 음식/간식 (예: 저당 간식, 알러지 프리 쿠키) — 영양·배려",
        "📚 학습 도구/문구 (예: 집중 노트, 시간 관리 스티커) — 자기주도 학습",
        "🎮 게임/놀이 (예: 협동 보드게임, 퍼즐) — 협동·논리력",
        "🌱 환경/생활 개선 (예: 재사용 키트, 절수·절전 아이템) — 환경 감수성",
        "💻 디지털/기술 (예: 앱/웹, 간단한 코딩 프로젝트) — 문제 해결·디지털 리터러시",
        "🤝 돌봄/커뮤니티 (예: 학교 상담 돕는 키트, 친구 챙김 캠페인) — 공감·배려",
        "🩺 건강/안전 (예: 응급 키트, 안전 알림 스티커) — 안전 의식",
        "기타 (직접 입력)"
    ]
    
    selected_option = st.radio(
        "아이디어 유형을 선택하세요:",
        idea_options,
        key="idea_selection"
    )
    
    # 예시 발명품 안내 섹션
    st.markdown("---")
    with st.expander("💡 창업(발명품)에 어려움을 느끼는 학생이 있나요? 선생님이 생각해 낸 아이디어를 참고해 보세요!", expanded=False):
        st.markdown("### 📋 선생님의 예시 발명품들")
        
        # 예시 1: 환경 개선 관련
        st.markdown("""
        #### 🌱 예시 1: 친환경 재사용 물병 스티커 키트
        
        **해결하려는 문제:**
        - 일회용 플라스틱 병 사용이 많아 환경 오염이 심각해요.
        - 학생들이 물병을 자주 잃어버려서 새로 사야 하는 상황이 반복돼요.
        
        **고려한 부분:**
        - 사용자: 초등학생들이 쉽게 사용할 수 있어야 함
        - 장소: 학교, 학원 등에서 휴대하기 편해야 함
        - 재료: 친환경 재료 사용 (재활용 종이, 식물성 접착제)
        - 시간: 5분 이내로 스티커를 붙일 수 있어야 함
        
        **중점으로 생각한 것:**
        - 환경 보호 의식 함양 (재사용 습관 만들기)
        - 개성 표현 (나만의 디자인)
        - 경제적 이점 (물병을 오래 사용)
        
        **주의점:**
        - 스티커가 물에 젖어도 떨어지지 않아야 함
        - 아이들이 안전하게 사용할 수 있는 재료여야 함
        - 너무 비싸지 않아야 함 (학생들이 부담 없이 구매 가능)
        
        **가격:**
        - 세트당 3,000원~5,000원 (스티커 10장 + 안내 책자 포함)
        
        **교육적 이점:**
        - 환경 감수성 향상
        - 책임감 배양 (물건을 소중히 다루는 습관)
        - 창의성 발휘 (나만의 디자인 만들기)
        """)
        
        st.markdown("---")
        
        # 예시 2: 학습 도구 관련
        st.markdown("""
        #### 📚 예시 2: 시간 관리 스마트 노트
        
        **해결하려는 문제:**
        - 숙제나 공부 계획을 세워도 자꾸 미루게 돼요.
        - 시간을 어떻게 쓰는지 스스로 파악하기 어려워요.
        
        **고려한 부분:**
        - 사용자: 초등학생이 스스로 체크할 수 있어야 함
        - 장소: 집, 학교 어디서나 사용 가능
        - 재료: 일반 노트보다 조금 두꺼운 종이, 색연필/스티커 포함
        - 시간: 하루 5분씩 체크하는 습관 형성
        
        **중점으로 생각한 것:**
        - 자기주도 학습 능력 향상
        - 시간 관리 습관 형성
        - 성취감 부여 (체크리스트 완성)
        
        **주의점:**
        - 너무 복잡하지 않아야 함 (아이들이 지루해하지 않도록)
        - 부모님의 지나친 간섭 없이 스스로 할 수 있어야 함
        - 가격이 너무 비싸면 학생들이 부담스러워함
        
        **가격:**
        - 노트 1권당 4,000원~6,000원 (체크 스티커 30장 포함)
        
        **교육적 이점:**
        - 자기주도 학습 능력 향상
        - 시간 관리 능력 배양
        - 목표 설정 및 달성 경험
        - 책임감 향상
        """)
        
        st.markdown("---")
        
        # 예시 3: 건강/안전 관련
        st.markdown("""
        #### 🩺 예시 3: 응급 상황 대처 가이드 스티커북
        
        **해결하려는 문제:**
        - 응급 상황에서 어떻게 해야 할지 몰라 당황해요.
        - 119에 전화할 때 뭐라고 말해야 할지 기억이 안 나요.
        
        **고려한 부분:**
        - 사용자: 초등학생이 쉽게 이해할 수 있어야 함
        - 장소: 집, 학교, 놀이터 등 어디서나 참고 가능
        - 재료: 방수 스티커, 그림이 많은 가이드북
        - 시간: 5분 안에 읽고 이해할 수 있어야 함
        
        **중점으로 생각한 것:**
        - 안전 의식 향상
        - 응급 상황 대처 능력
        - 생명을 소중히 여기는 마음
        
        **주의점:**
        - 너무 무서운 내용이면 아이들이 두려워할 수 있음
        - 실제로 도움이 되는 정확한 정보여야 함
        - 부모님과 함께 읽을 수 있는 구성
        
        **가격:**
        - 스티커북 1권당 5,000원~7,000원 (가이드북 + 응급 전화 스티커 포함)
        
        **교육적 이점:**
        - 안전 의식 향상
        - 문제 해결 능력 향상
        - 책임감 배양
        - 생명 존중 의식 함양
        """)
        
        st.info("💡 위 예시들을 참고해서, 여러분만의 창의적인 아이디어를 생각해보세요!")
    
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
                
                # 즉시 Gemini 응답 생성
                with st.spinner("선생님이 아이디어를 검토하고 있습니다..."):
                    time.sleep(1.2)
                    try:
                        ai_reply = call_gemini(st.session_state.messages, category)
                        st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                    except RuntimeError as e:
                        st.error(str(e))
                        st.stop()
                st.rerun()
    else:
        if st.button("선택 완료", type="primary", use_container_width=True):
            # 선택지에서 이모지와 설명 제거하고 핵심 키워드만 추출
            clean_option = selected_option.split("(")[0].strip()
            user_input = f"저는 {clean_option} 관련 아이디어를 생각해보고 싶어요."
            st.session_state.idea_selected = True
            st.session_state.messages.append({"role": "user", "content": user_input})
            
            # 즉시 Gemini 응답 생성
            with st.spinner("선생님이 아이디어를 검토하고 있습니다..."):
                time.sleep(1.2)
                try:
                    ai_reply = call_gemini(st.session_state.messages, category)
                    st.session_state.messages.append({"role": "assistant", "content": ai_reply})
                except RuntimeError as e:
                    st.error(str(e))
                    st.stop()
                st.rerun()

# 대화 기록 시각화는 선택지가 선택된 후에만
if st.session_state.idea_selected:
    for message in st.session_state.messages:
        if message["role"] != "system":
            avatar = "👩‍🏫" if message["role"] == "assistant" else "🧒"
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])

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
            try:
                ai_reply = call_gemini(st.session_state.messages, category)
            except RuntimeError as e:
                st.error(str(e))
                st.stop()

        # 3. AI 답변 표시
        st.chat_message("assistant", avatar="👩‍🏫").markdown(ai_reply)
        st.session_state.messages.append({"role": "assistant", "content": ai_reply})

        # 4. [보상 시스템] 성취감 부여
        # 선생님의 칭찬 키워드가 있을 때만 축하 효과
        positive_keywords = ["훌륭합니다", "정확합니다", "통과", "잘했습니다", "탁월합니다"]
        if any(keyword in ai_reply for keyword in positive_keywords):
            st.balloons()
            st.success("🎉 통과! 아주 논리적인 수정이었습니다. 상담 일지를 저장하세요.")
