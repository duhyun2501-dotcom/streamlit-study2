import streamlit as st

st.set_page_config(page_title="대시보드 모음", page_icon="📊")

marketing  = st.Page("pages/marketing.py",  title="마케팅 캠페인", icon="📣")
ecommerce  = st.Page("pages/ecommerce.py",  title="이커머스 매출",  icon="🛒")

pg = st.navigation([marketing, ecommerce])
pg.run()