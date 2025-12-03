import streamlit as st
import requests
import os
from dotenv import load_dotenv

# .env 파일에서 API 키 로드
load_dotenv()

# 페이지 설정
st.set_page_config(
    page_title="Gemini 챗봇",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Google Gemini 챗봇")
st.markdown("---")

# 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []

# 사이드바에 API 키 입력 필드 추가
with st.sidebar:
    st.header("⚙️ 설정")
    
    # .env에서 기본값 로드
    default_api_key = os.getenv("GOOGLE_API_KEY", "")
    if default_api_key == "your_google_api_key_here":
        default_api_key = ""
    
    # API 키 입력
    api_key = st.text_input(
        "Google API Key",
        value=default_api_key,
        type="password",
        help="Google Gemini API 키를 입력하세요. .env 파일에 설정되어 있으면 자동으로 로드됩니다.",
        placeholder="API 키를 입력하세요..."
    )
    
    st.markdown("---")
    
    st.header("ℹ️ 정보")
    st.markdown("""
    **Google Gemini 2.5 Flash** 모델을 사용하는 챗봇입니다.
    
    ### 사용 방법
    1. 위에 API Key를 입력하세요
    2. 아래 입력창에 메시지를 입력하세요
    3. Enter를 누르거나 전송 버튼을 클릭하세요
    4. AI의 응답을 확인하세요
    
    ### 기능
    - 대화 기록 유지
    - 실시간 응답 생성
    - 모던한 UI
    """)
    
    if st.button("🗑️ 대화 기록 지우기"):
        st.session_state.messages = []
        st.rerun()

# API 키 확인
if not api_key or api_key.strip() == "":
    st.warning("⚠️ 사이드바에서 Google API Key를 입력해주세요!")
    st.info("💡 API Key는 Google Cloud Console에서 발급받을 수 있습니다.")
    st.stop()

# 채팅 기록 표시
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 사용자 입력
if prompt := st.chat_input("메시지를 입력하세요..."):
    # 사용자 메시지 추가
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Gemini API 호출
    with st.chat_message("assistant"):
        with st.spinner("응답을 생성하는 중..."):
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
                
                headers = {
                    "Content-Type": "application/json"
                }
                
                # System Instruction 설정
                system_instruction = """당신은 친절하지만 카리스마 있는 초등학교 선생님입니다.

성격과 말투:
- 기본적으로 따뜻하고 다정하지만, 필요하면 단호하고 무게감 있게 말합니다.
- 아이들을 진심으로 아끼되, 규칙과 원칙은 흔들림 없이 지킵니다.
- 위트 있는 표현을 살짝 섞지만, 과한 장난은 삼가고 진지함을 잃지 않습니다.
- 이모지는 꼭 필요할 때만 드물게 사용합니다.

대화 스타일:
- 초등학생도 이해하기 쉬운 말로 차근차근 설명합니다.
- 칭찬과 격려는 아끼지 않지만, 잘못된 부분은 분명하게 짚어줍니다.
- 때때로 “선생님이 말하는데~” 같은 표현을 자연스럽게 사용합니다.
- 학생이 스스로 생각하도록 질문을 던지고, 실천 가능한 조언을 제공합니다."""

                # 대화 기록을 컨텍스트로 포함
                contents = []
                for msg in st.session_state.messages[-10:]:  # 최근 10개 메시지만 사용
                    if msg["role"] == "user":
                        contents.append({
                            "role": "user",
                            "parts": [{"text": msg["content"]}]
                        })
                    elif msg["role"] == "assistant":
                        contents.append({
                            "role": "model",
                            "parts": [{"text": msg["content"]}]
                        })
                
                data = {
                    "contents": contents,
                    "systemInstruction": {
                        "parts": [{"text": system_instruction}]
                    }
                }
                
                response = requests.post(url, headers=headers, json=data)
                response.raise_for_status()
                
                result = response.json()
                
                if "candidates" in result and len(result["candidates"]) > 0:
                    assistant_response = result["candidates"][0]["content"]["parts"][0]["text"]
                    st.markdown(assistant_response)
                    st.session_state.messages.append({"role": "assistant", "content": assistant_response})
                else:
                    st.error("응답을 받을 수 없습니다.")
                    
            except requests.exceptions.RequestException as e:
                st.error(f"API 요청 중 오류가 발생했습니다: {str(e)}")
            except Exception as e:
                st.error(f"오류가 발생했습니다: {str(e)}")

