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

# API 키 확인
api_key = os.getenv("GOOGLE_API_KEY")

if not api_key or api_key == "your_google_api_key_here":
    st.error("⚠️ .env 파일에 GOOGLE_API_KEY를 설정해주세요!")
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
                    "contents": contents
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

# 사이드바에 정보 표시
with st.sidebar:
    st.header("ℹ️ 정보")
    st.markdown("""
    **Google Gemini 2.5 Flash** 모델을 사용하는 챗봇입니다.
    
    ### 사용 방법
    1. 아래 입력창에 메시지를 입력하세요
    2. Enter를 누르거나 전송 버튼을 클릭하세요
    3. AI의 응답을 확인하세요
    
    ### 기능
    - 대화 기록 유지
    - 실시간 응답 생성
    - 모던한 UI
    """)
    
    if st.button("🗑️ 대화 기록 지우기"):
        st.session_state.messages = []
        st.rerun()

