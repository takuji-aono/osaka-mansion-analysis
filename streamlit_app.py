
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# ページ設定
st.set_page_config(
    page_title="大阪市24区 中古マンション投資分析アプリ",
    page_icon="🏢",
    layout="wide"
)

# タイトル
st.title("🏢 大阪市24区 中古マンション投資戦略分析アプリ")
st.markdown("---")

# データ読み込み
@st.cache_data
def load_data():
    df = pd.read_csv("data/osaka_mansion_cleaned.csv")
    return df

df = load_data()

# サイドバー - フィルター
st.sidebar.header("🔍 検索条件")

# 区の選択
wards = ["全て"] + sorted(df["市区町村名"].unique().tolist())
selected_ward = st.sidebar.multiselect(
    "区を選択",
    options=wards,
    default=["全て"]
)

# 面積の範囲
area_min, area_max = st.sidebar.slider(
    "面積（㎡）",
    min_value=int(df["面積（㎡）"].min()),
    max_value=int(df["面積（㎡）"].max()),
    value=(30, 100)
)

# 築年数の範囲
age_min, age_max = st.sidebar.slider(
    "築年数",
    min_value=int(df["築年数"].min()),
    max_value=int(df["築年数"].max()),
    value=(0, 35)
)

# 駅距離の範囲
distance_min, distance_max = st.sidebar.slider(
    "最寄駅距離（分）",
    min_value=int(df["最寄駅：距離（分）"].min()),
    max_value=int(df["最寄駅：距離（分）"].max()),
    value=(0, 12)
)

# データフィルタリング
filtered_df = df.copy()

if "全て" not in selected_ward:
    filtered_df = filtered_df[filtered_df["市区町村名"].isin(selected_ward)]

filtered_df = filtered_df[
    (filtered_df["面積（㎡）"] >= area_min) &
    (filtered_df["面積（㎡）"] <= area_max) &
    (filtered_df["築年数"] >= age_min) &
    (filtered_df["築年数"] <= age_max) &
    (filtered_df["最寄駅：距離（分）"] >= distance_min) &
    (filtered_df["最寄駅：距離（分）"] <= distance_max)
]

# メインエリア
st.sidebar.markdown("---")
st.sidebar.metric("絞り込み結果", f"{len(filtered_df):,}件", f"全体の{len(filtered_df)/len(df)*100:.1f}%")

# タブ作成
tab1, tab2, tab3, tab4 = st.tabs(["📊 概要", "🗺️ 地域分析", "💰 投資シミュレーション", "📥 データダウンロード"])

# タブ1: 概要
with tab1:
    st.header("📊 データ概要")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "平均平米単価",
            f"{filtered_df['平米単価'].mean():.2f}万円/㎡"
        )
    
    with col2:
        st.metric(
            "平均取引価格",
            f"{filtered_df['取引価格（総額）'].mean()/10000:.0f}万円"
        )
    
    with col3:
        st.metric(
            "平均面積",
            f"{filtered_df['面積（㎡）'].mean():.1f}㎡"
        )
    
    with col4:
        st.metric(
            "平均築年数",
            f"{filtered_df['築年数'].mean():.1f}年"
        )
    
    st.markdown("---")
    
    # グラフ1: 平米単価の分布
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("平米単価の分布")
        fig1 = px.histogram(
            filtered_df,
            x="平米単価",
            nbins=50,
            title="平米単価の分布",
            labels={"平米単価": "平米単価（万円/㎡）", "count": "件数"}
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        st.subheader("取引価格の分布")
        fig2 = px.histogram(
            filtered_df,
            x="取引価格（総額）",
            nbins=50,
            title="取引価格の分布",
            labels={"取引価格（総額）": "取引価格（万円）", "count": "件数"}
        )
        st.plotly_chart(fig2, use_container_width=True)
    
    # グラフ2: 面積と平米単価の関係
    st.subheader("面積と平米単価の関係")
    fig3 = px.scatter(
        filtered_df,
        x="面積（㎡）",
        y="平米単価",
        color="市区町村名",
        hover_data=["築年数", "最寄駅：距離（分）"],
        title="面積と平米単価の関係",
        labels={"面積（㎡）": "面積（㎡）", "平米単価": "平米単価（万円/㎡）"}
    )
    st.plotly_chart(fig3, use_container_width=True)

# タブ2: 地域分析
with tab2:
    st.header("🗺️ 地域別分析")
    
    # 区別の統計
    ward_stats = filtered_df.groupby("市区町村名").agg({
        "平米単価": "mean",
        "取引価格（総額）": "mean",
        "面積（㎡）": "mean",
        "築年数": "mean",
        "最寄駅：距離（分）": "mean",
        "市区町村名": "count"
    }).rename(columns={"市区町村名": "件数"}).reset_index()
    
    ward_stats = ward_stats.sort_values("平米単価", ascending=False)
    
    # グラフ: 区別平米単価ランキング
    st.subheader("区別平米単価ランキング")
    fig4 = px.bar(
        ward_stats,
        x="市区町村名",
        y="平米単価",
        color="平米単価",
        title="区別平米単価ランキング",
        labels={"市区町村名": "区", "平米単価": "平均平米単価（万円/㎡）"},
        color_continuous_scale="RdYlGn_r"
    )
    st.plotly_chart(fig4, use_container_width=True)
    
    # 区別統計テーブル
    st.subheader("区別詳細統計")
    st.dataframe(
        ward_stats.style.format({
            "平米単価": "{:.2f}万円/㎡",
            "取引価格（総額）": "{:.0f}万円",
            "面積（㎡）": "{:.1f}㎡",
            "築年数": "{:.1f}年",
            "最寄駅：距離（分）": "{:.1f}分",
            "件数": "{:.0f}件"
        }),
        use_container_width=True
    )

# タブ3: 投資シミュレーション
with tab3:
    st.header("💰 投資シミュレーション")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("物件条件")
        sim_price = st.number_input("購入価格（万円）", min_value=500, max_value=10000, value=3000, step=100)
        sim_rent = st.number_input("想定月額賃料（万円）", min_value=5, max_value=50, value=12, step=1)
        sim_cost = st.number_input("年間経費率（%）", min_value=10, max_value=50, value=20, step=5)
    
    with col2:
        st.subheader("計算結果")
        
        # 表面利回り
        gross_yield = (sim_rent * 12) / sim_price * 100
        st.metric("表面利回り", f"{gross_yield:.2f}%")
        
        # 実質利回り
        net_yield = ((sim_rent * 12) * (1 - sim_cost/100)) / sim_price * 100
        st.metric("実質利回り", f"{net_yield:.2f}%")
        
        # 年間キャッシュフロー
        annual_cashflow = (sim_rent * 12) * (1 - sim_cost/100)
        st.metric("年間キャッシュフロー", f"{annual_cashflow:.0f}万円")
        
        # 投資回収年数
        payback = sim_price / annual_cashflow
        st.metric("投資回収年数", f"{payback:.1f}年")
    
    st.markdown("---")
    
    # 利回り比較グラフ
    st.subheader("利回り比較（面積帯別）")
    
    # 面積帯別の平均値を計算
    area_bins = [30, 50, 70, 100]
    area_labels = ["30-50㎡", "50-70㎡", "70-100㎡"]
    filtered_df["面積帯"] = pd.cut(filtered_df["面積（㎡）"], bins=area_bins, labels=area_labels)
    
    area_yield = filtered_df.groupby("面積帯")["平米単価"].mean().reset_index()
    
    # 想定利回りを計算（簡易版）
    area_yield["想定表面利回り"] = (12 * 12) / (area_yield["平米単価"] * 60) * 100  # 60㎡を基準
    
    fig5 = px.bar(
        area_yield,
        x="面積帯",
        y="想定表面利回り",
        title="面積帯別の想定表面利回り",
        labels={"面積帯": "面積帯", "想定表面利回り": "想定表面利回り（%）"},
        text="想定表面利回り"
    )
    fig5.update_traces(texttemplate='%{text:.2f}%', textposition='outside')
    st.plotly_chart(fig5, use_container_width=True)
    
    # 投資戦略の推奨
    st.markdown("---")
    st.subheader("📋 投資戦略の推奨")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.info("""
        **🔰 初心者向け**
        - 予算: 2,000-3,000万円
        - エリア: 天王寺区、阿倍野区
        - 面積: 30-50㎡
        - 期待利回り: 4.5-5.5%
        """)
    
    with col2:
        st.success("""
        **⭐ 中級者向け**
        - 予算: 3,000-5,000万円
        - エリア: 中央区、西区
        - 面積: 50-70㎡
        - 期待利回り: 5.0-6.0%
        """)
    
    with col3:
        st.warning("""
        **💎 上級者向け**
        - 予算: 5,000万円以上
        - エリア: 北区、中央区
        - 面積: 70-100㎡
        - 期待利回り: 4.0-5.0%
        """)

# タブ4: データダウンロード
with tab4:
    st.header("📥 データダウンロード")
    
    st.write(f"現在の絞り込み結果: **{len(filtered_df):,}件**")
    
    # ダウンロードボタン
    csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
    
    st.download_button(
        label="📥 CSVダウンロード",
        data=csv,
        file_name=f"osaka_mansion_filtered_{len(filtered_df)}.csv",
        mime="text/csv"
    )
    
    st.markdown("---")
    
    # データプレビュー
    st.subheader("データプレビュー（上位20件）")
    st.dataframe(
        filtered_df.head(20).style.format({
            "取引価格（総額）": "{:.0f}万円",
            "平米単価": "{:.2f}万円/㎡",
            "面積（㎡）": "{:.1f}㎡",
            "築年数": "{:.0f}年",
            "最寄駅：距離（分）": "{:.0f}分"
        }),
        use_container_width=True
    )

# フッター
st.markdown("---")
st.markdown("""
### 📌 注意事項
- 本アプリの分析結果は投資判断の参考情報です
- 最終的な投資判断は、個別物件の詳細調査と専門家への相談を推奨します
- データ出典: 国土交通省不動産取引価格情報（2020年Q1～2024年Q2）

**作成者:** データサイエンス分析プロジェクト  
**作成日:** 2026年2月
""")
