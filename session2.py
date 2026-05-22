# 세션 스테이트 key 패턴
import streamlit as st

# 웨젯의 매개변수로 key를 지정할 경우
# key='age_range' → st.session_state['age_range']에 자동 저장
# 초기화 가드 대신
#  최초 실행 시 value 값(0, 80)을 초기값으로 사용.
# 데이터 변경 시 -> rerun -> 마지막 session state 값으로 불러옴.
age_range = st.slider("나이 범위", 0, 80, (0, 80), key='age_range')

# 읽기
st.write("현재 선택 값:", st.session_state['age_range'])

