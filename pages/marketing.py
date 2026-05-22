import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="📣 마케팅 캠페인 대시보드", layout="wide")

@st.cache_data
def load_marketing():
    df = pd.read_csv('data/marketing_campaign_dataset.csv')
    df['Acquisition_Cost'] = (
        df['Acquisition_Cost']
        .str.replace('[$,]', '', regex=True)
        .astype(float)
    )
    df['Date'] = pd.to_datetime(df['Date'])
    df['Month'] = df['Date'].dt.to_period('M').astype(str)
    df['Quarter'] = df['Date'].dt.to_period('Q').astype(str)
    df['CTR'] = df['Clicks'] / df['Impressions']
    return df

df = load_marketing().copy()

# ── 사이드바 필터 ──────────────────────────────────────────
with st.sidebar:
    st.header("🔧 필터")
    if st.button("필터 초기화"):
        st.session_state['campaign_types'] = df['Campaign_Type'].unique().tolist()
        st.session_state['location'] = "전체"
        st.session_state['channel'] = "전체"

    campaign_types = st.multiselect(
        "캠페인 유형",
        df['Campaign_Type'].unique().tolist(),
        default=st.session_state.get('campaign_types', df['Campaign_Type'].unique().tolist()),
        key='campaign_types'
    )
    location = st.selectbox(
        "지역",
        ["전체"] + sorted(df['Location'].unique().tolist()),
        key='location'
    )
    channel = st.selectbox(
        "채널",
        ["전체"] + sorted(df['Channel_Used'].unique().tolist()),
        key='channel'
    )

# ── 필터 적용 ──────────────────────────────────────────────
filtered = df[df['Campaign_Type'].isin(campaign_types)]
if location != "전체":
    filtered = filtered[filtered['Location'] == location]
if channel != "전체":
    filtered = filtered[filtered['Channel_Used'] == channel]

# ── 제목 ──────────────────────────────────────────────────
st.title("📣 마케팅 캠페인 대시보드")
st.write(f"전체 데이터: {len(df):,}행 | 필터 적용: {len(filtered):,}행")

# ── 요약 지표 ─────────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("총 캠페인 수", f"{len(filtered):,}")
col2.metric("평균 ROI", f"{filtered['ROI'].mean():.2f}")
col3.metric("평균 전환율", f"{filtered['Conversion_Rate'].mean():.1%}")
col4.metric("평균 획득 비용", f"${filtered['Acquisition_Cost'].mean():,.0f}")
col5.metric("평균 Engagement", f"{filtered['Engagement_Score'].mean():.1f}")

st.divider()

# ── 탭 구성 ───────────────────────────────────────────────
tab1, tab2, tab4, tab5 = st.tabs([
    "📈 시계열 분석",
    "📡 채널 분석",
    "👥 타겟/세그먼트",
    "🌍 지역 분석",
])

# ── Tab1: 시계열 분석 ──────────────────────────────────────
with tab1:
    st.subheader("시계열 분석")

    time_unit = st.radio("단위 선택", ["월별", "분기별"], horizontal=True)
    group_col = 'Month' if time_unit == "월별" else 'Quarter'

    ts = filtered.groupby(group_col).agg(
        ROI=('ROI', 'mean'),
        Conversion_Rate=('Conversion_Rate', 'mean'),
        Clicks=('Clicks', 'sum')
    ).reset_index()

    fig1 = px.line(ts, x=group_col, y='ROI', title=f'{time_unit} 평균 ROI 추이', markers=True)
    st.plotly_chart(fig1, use_container_width=True)

    fig2 = px.line(ts, x=group_col, y='Conversion_Rate', title=f'{time_unit} 평균 전환율 추이',
                   markers=True, color_discrete_sequence=['#EF553B'])
    st.plotly_chart(fig2, use_container_width=True)

# ── Tab2: 채널 분석 ────────────────────────────────────────
with tab2:
    st.subheader("채널 분석")

    col1, col2 = st.columns(2)
    with col1:
        ch_clicks = filtered.groupby('Channel_Used')['Clicks'].sum().reset_index()
        fig = px.bar(ch_clicks, x='Channel_Used', y='Clicks', title='채널별 총 클릭수',
                     color='Channel_Used')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        ch_impressions = filtered.groupby('Channel_Used')['Impressions'].sum().reset_index()
        fig = px.bar(ch_impressions, x='Channel_Used', y='Impressions', title='채널별 총 노출수',
                     color='Channel_Used')
        st.plotly_chart(fig, use_container_width=True)

    ch_engage = filtered.groupby('Channel_Used')['Engagement_Score'].mean().reset_index()
    fig = px.bar(ch_engage, x='Channel_Used', y='Engagement_Score',
                 title='채널별 평균 Engagement Score', color='Channel_Used')
    st.plotly_chart(fig, use_container_width=True)

    ch_ctr = filtered.groupby('Channel_Used')['CTR'].mean().reset_index()
    fig = px.bar(ch_ctr, x='Channel_Used', y='CTR', title='채널별 평균 클릭률 (CTR)',
                 color='Channel_Used')
    st.plotly_chart(fig, use_container_width=True)

# ── Tab4: 타겟/세그먼트 ────────────────────────────────────
with tab4:
    st.subheader("타겟 오디언스 & 고객 세그먼트 분석")

    col1, col2 = st.columns(2)
    with col1:
        ta = filtered.groupby('Target_Audience')['Conversion_Rate'].mean().reset_index()
        fig = px.bar(ta, x='Target_Audience', y='Conversion_Rate',
                     title='타겟 오디언스별 평균 전환율', color='Target_Audience')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        cs = filtered.groupby('Customer_Segment')['ROI'].mean().reset_index()
        fig = px.bar(cs, x='Customer_Segment', y='ROI',
                     title='고객 세그먼트별 평균 ROI', color='Customer_Segment')
        st.plotly_chart(fig, use_container_width=True)

    lang = filtered.groupby('Language')['Engagement_Score'].mean().reset_index()
    fig = px.bar(lang, x='Language', y='Engagement_Score',
                 title='언어별 평균 Engagement Score', color='Language')
    st.plotly_chart(fig, use_container_width=True)

# ── Tab5: 지역 분석 ────────────────────────────────────────
with tab5:
    st.subheader("지역 분석")

    col1, col2 = st.columns(2)
    with col1:
        loc_roi = filtered.groupby('Location')['ROI'].mean().reset_index()
        fig = px.bar(loc_roi, x='Location', y='ROI', title='지역별 평균 ROI', color='Location')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        loc_cv = filtered.groupby('Location')['Conversion_Rate'].mean().reset_index()
        fig = px.bar(loc_cv, x='Location', y='Conversion_Rate',
                     title='지역별 평균 전환율', color='Location')
        st.plotly_chart(fig, use_container_width=True)

    loc_ch = filtered.groupby(['Location', 'Channel_Used']).size().reset_index(name='count')
    fig = px.bar(loc_ch, x='Location', y='count', color='Channel_Used',
                 title='지역별 채널 사용 분포', barmode='stack')
    st.plotly_chart(fig, use_container_width=True)