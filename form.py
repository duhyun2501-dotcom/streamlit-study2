# 폼

import streamlit as st

with st.form("filter_form"):
    campaign_type = st.selectbox("캠페인 유형", ["Email", "Influencer", "Display"])
    min_roi       = st.slider("최소 ROI", 0.0, 10.0, 0.0)
    submitted     = st.form_submit_button("검색 적용")

# 제출버튼이 클릭되었을때 True
# 반드시 form 밖에서만 실행
if submitted:
    st.write(f"{campaign_type} / ROI >= {min_roi}")