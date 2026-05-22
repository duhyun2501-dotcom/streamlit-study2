import streamlit as st
import pandas as pd
import plotly.express as px

@st.cache_data
def load_ecommerce():
    df = pd.read_csv('data/ecommerce_sales_data.csv', index_col=0)
    df['City'] = df['City'].str.strip()
    df['Order Date'] = pd.to_datetime(df['Order Date'], dayfirst=True)
    return df

df = load_ecommerce().copy()
st.title("🛒 이커머스 매출 대시보드")

# ── 사이드바 필터 ──────────────────────────────────────────
with st.sidebar:
    st.header("🔧 필터")
    if st.button("필터 초기화"):
        st.session_state['categories'] = df['Product Category'].unique().tolist()
        st.session_state['month_range'] = (1, 12)

    categories = st.multiselect(
        "카테고리",
        df['Product Category'].unique().tolist(),
        default=st.session_state.get('categories', df['Product Category'].unique().tolist()),
        key='categories'
    )
    month_range = st.slider("월 범위", 1, 12, (1, 12), key='month_range')

# ── 필터 적용 ──────────────────────────────────────────────
filtered = df[
    df['Product Category'].isin(categories) &
    df['Month'].between(month_range[0], month_range[1])
]

# ── 요약 지표 ─────────────────────────────────────────────
col1, col2, col3 = st.columns(3)
col1.metric("총 주문 수", f"{len(filtered):,}")
col2.metric("총 매출", f"${filtered['Sales'].sum():,.0f}")
col3.metric("평균 주문 금액", f"${filtered['Sales'].mean():,.0f}")

st.divider()

# ── 탭 구성 ───────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 카테고리 분석",
    "🕐 시간대 분석",
    "📦 상품 분석",
    "🏙️ 도시 분석",
])

# ── Tab1: 카테고리 분석 (기존) ─────────────────────────────
with tab1:
    st.subheader("카테고리별 총 매출")
    fig = px.bar(
        filtered.groupby('Product Category')['Sales'].sum().reset_index(),
        x='Product Category', y='Sales',
        title='카테고리별 총 매출', color='Product Category'
    )
    st.plotly_chart(fig, use_container_width=True)

# ── Tab2: 시간대 분석 ─────────────────────────────────────
with tab2:
    st.subheader("시간대 분석")

    col1, col2 = st.columns(2)
    with col1:
        tod = filtered.groupby('Time of Day')['Sales'].sum().reset_index()
        order = ['Morning', 'Afternoon', 'Evening', 'Night']
        tod['Time of Day'] = pd.Categorical(tod['Time of Day'], categories=order, ordered=True)
        tod = tod.sort_values('Time of Day')
        fig = px.bar(tod, x='Time of Day', y='Sales',
                     title='시간대별 총 매출', color='Time of Day')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        tod_count = filtered.groupby('Time of Day').size().reset_index(name='주문수')
        tod_count['Time of Day'] = pd.Categorical(tod_count['Time of Day'], categories=order, ordered=True)
        tod_count = tod_count.sort_values('Time of Day')
        fig = px.bar(tod_count, x='Time of Day', y='주문수',
                     title='시간대별 주문 건수', color='Time of Day')
        st.plotly_chart(fig, use_container_width=True)

    hour = filtered.groupby('Hour')['Sales'].sum().reset_index()
    fig = px.line(hour, x='Hour', y='Sales', markers=True,
                  title='시간(Hour)별 매출 추이')
    fig.update_xaxes(dtick=1)
    st.plotly_chart(fig, use_container_width=True)

# ── Tab3: 상품 분석 ────────────────────────────────────────
with tab3:
    st.subheader("상품 분석")

    col1, col2 = st.columns(2)
    with col1:
        top_sales = (
            filtered.groupby('Product')['Sales']
            .sum().reset_index()
            .sort_values('Sales', ascending=False)
            .head(10)
        )
        fig = px.bar(top_sales, x='Sales', y='Product', orientation='h',
                     title='매출 Top 10 상품', color='Sales',
                     color_continuous_scale='Blues')
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        top_qty = (
            filtered.groupby('Product')['Quantity Ordered']
            .sum().reset_index()
            .sort_values('Quantity Ordered', ascending=False)
            .head(10)
        )
        fig = px.bar(top_qty, x='Quantity Ordered', y='Product', orientation='h',
                     title='판매량 Top 10 상품', color='Quantity Ordered',
                     color_continuous_scale='Greens')
        fig.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig, use_container_width=True)

    price_qty = filtered.groupby('Product').agg(
        avg_price=('Price Each', 'mean'),
        total_qty=('Quantity Ordered', 'sum')
    ).reset_index()
    fig = px.scatter(price_qty, x='avg_price', y='total_qty',
                     hover_name='Product', title='상품 평균 단가 vs 판매량',
                     labels={'avg_price': '평균 단가', 'total_qty': '총 판매량'},
                     size='total_qty', color='total_qty',
                     color_continuous_scale='Viridis')
    st.plotly_chart(fig, use_container_width=True)

# ── Tab4: 도시 분석 ────────────────────────────────────────
with tab4:
    st.subheader("도시 분석")

    col1, col2 = st.columns(2)
    with col1:
        city_sales = filtered.groupby('City')['Sales'].sum().reset_index().sort_values('Sales', ascending=False)
        fig = px.bar(city_sales, x='City', y='Sales',
                     title='도시별 총 매출', color='City')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        city_count = filtered.groupby('City').size().reset_index(name='주문수').sort_values('주문수', ascending=False)
        fig = px.bar(city_count, x='City', y='주문수',
                     title='도시별 주문 건수', color='City')
        st.plotly_chart(fig, use_container_width=True)

    city_cat = filtered.groupby(['City', 'Product Category']).size().reset_index(name='count')
    fig = px.bar(city_cat, x='City', y='count', color='Product Category',
                 title='도시별 카테고리 분포', barmode='stack')
    st.plotly_chart(fig, use_container_width=True)