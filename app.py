"""
파생상품 시뮬레이션 대시보드 - 메인 애플리케이션

Streamlit을 사용한 인터랙티브 금융 파생상품 시뮬레이션 대시보드
"""

import streamlit as st
import sys
import os

# 경로 설정
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from models.black_scholes import BlackScholesModel
from models.futures import FuturesModel
from utils.visualization import create_payoff_diagram, create_greeks_heatmap

# 페이지 설정
st.set_page_config(
    page_title="파생상품 시뮬레이션 대시보드",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        padding-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# 헤더
st.markdown('<div class="main-header">📊 파생상품 시뮬레이션 대시보드</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Financial Derivatives Simulation Dashboard</div>', unsafe_allow_html=True)

# 사이드바 메뉴
st.sidebar.title("📑 메뉴")
menu = st.sidebar.selectbox(
    "분석 도구 선택",
    ["🏠 홈", "📈 옵션 계산기", "📊 선물 계산기", "🎯 Greeks 분석", "📚 이론 설명"]
)

st.sidebar.markdown("---")
st.sidebar.info(
    """
    **교육용 도구**

    이 대시보드는 교육 목적으로만 사용되며,
    실제 투자 결정을 위한 것이 아닙니다.
    """
)

# ===== 홈 화면 =====
if menu == "🏠 홈":
    st.header("환영합니다! 👋")

    st.markdown("""
    이 대시보드는 **금융 파생상품**의 가격 계산 및 시뮬레이션을 위한 교육용 도구입니다.

    ### ✨ 주요 기능

    - **옵션 계산기**: Black-Scholes 모델을 사용한 콜/풋 옵션 가격 계산
    - **선물 계산기**: 이론적 선물 가격 및 베이시스 분석
    - **Greeks 분석**: Delta, Gamma, Theta, Vega, Rho 민감도 분석
    - **손익 시뮬레이션**: 다양한 시나리오에서의 손익 분석

    ### 📚 주요 개념

    왼쪽 사이드바에서 원하는 분석 도구를 선택하세요.
    """)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.info("""
        **옵션 (Options)**

        특정 가격에 자산을 사거나 팔 수 있는 권리
        - 콜 옵션: 살 권리
        - 풋 옵션: 팔 권리
        """)

    with col2:
        st.info("""
        **선물 (Futures)**

        미래에 특정 가격으로 자산을 사거나 팔 의무
        - 표준화된 계약
        - 일일정산
        """)

    with col3:
        st.info("""
        **Greeks**

        옵션 가격의 민감도 지표
        - Delta: 가격 민감도
        - Gamma: Delta 변화율
        - Theta: 시간 가치 감소
        """)

# ===== 옵션 계산기 =====
elif menu == "📈 옵션 계산기":
    st.header("📈 옵션 가격 계산기")
    st.markdown("Black-Scholes 모델을 사용한 유럽형 옵션 가격 계산")

    col1, col2, col3 = st.columns(3)

    with col1:
        S = st.number_input("기초자산 가격 ($)", value=100.0, min_value=0.01, step=1.0)
        K = st.number_input("행사가격 ($)", value=105.0, min_value=0.01, step=1.0)

    with col2:
        T_days = st.number_input("만기 (일)", value=30, min_value=1, step=1)
        T = T_days / 365
        r = st.number_input("무위험이자율 (%)", value=5.0, min_value=0.0, max_value=100.0, step=0.1) / 100

    with col3:
        sigma = st.number_input("변동성 (%)", value=20.0, min_value=0.1, max_value=200.0, step=0.5) / 100
        option_type = st.selectbox("옵션 타입", ["Call", "Put"])

    if st.button("💰 계산하기", type="primary"):
        try:
            bs = BlackScholesModel(S, K, T, r, sigma)

            # 옵션 가격
            call_price = bs.call_price()
            put_price = bs.put_price()

            # Greeks
            greeks = bs.get_all_greeks(option_type.lower())

            # 결과 표시
            st.markdown("---")
            st.subheader("💰 계산 결과")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("콜 옵션 가격", f"${call_price:.4f}")
            with col2:
                st.metric("풋 옵션 가격", f"${put_price:.4f}")
            with col3:
                intrinsic = bs.intrinsic_value(option_type.lower())
                st.metric("내재가치", f"${intrinsic:.4f}")
            with col4:
                time_val = bs.time_value(option_type.lower())
                st.metric("시간가치", f"${time_val:.4f}")

            # Greeks 표시
            st.markdown("---")
            st.subheader("📊 Greeks")

            greeks_col1, greeks_col2, greeks_col3 = st.columns(3)

            with greeks_col1:
                st.metric("Delta (Δ)", f"{greeks['delta']:.4f}")
                st.metric("Gamma (Γ)", f"{greeks['gamma']:.4f}")

            with greeks_col2:
                st.metric("Theta (Θ) - 연간", f"{greeks['theta']:.4f}")
                st.metric("Theta (Θ) - 일일", f"{greeks['theta_daily']:.4f}")

            with greeks_col3:
                st.metric("Vega (ν)", f"{greeks['vega']:.4f}")
                st.metric("Rho (ρ)", f"{greeks['rho']:.4f}")

            # 손익 다이어그램
            st.markdown("---")
            st.subheader("📉 손익 다이어그램")

            price = call_price if option_type.lower() == 'call' else put_price
            fig = create_payoff_diagram(S, K, price, option_type.lower(), 'long')
            st.plotly_chart(fig, use_container_width=True)

            # 설명
            st.info(f"""
            **{option_type} 옵션 분석 결과**

            - 현재 옵션은 {'ITM (In-The-Money)' if intrinsic > 0 else 'OTM (Out-of-The-Money)' if intrinsic == 0 else 'ATM (At-The-Money)'}입니다.
            - Delta는 {greeks['delta']:.4f}로, 기초자산 가격이 $1 상승하면 옵션 가격은 약 ${abs(greeks['delta']):.4f} {'상승' if greeks['delta'] > 0 else '하락'}합니다.
            - Theta는 하루에 약 ${abs(greeks['theta_daily']):.4f}의 시간 가치가 감소합니다.
            """)

        except Exception as e:
            st.error(f"계산 중 오류가 발생했습니다: {str(e)}")

# ===== 선물 계산기 =====
elif menu == "📊 선물 계산기":
    st.header("📊 선물 가격 계산기")
    st.markdown("이론적 선물 가격 및 베이시스 분석")

    col1, col2 = st.columns(2)

    with col1:
        S = st.number_input("현물 가격 ($)", value=100.0, min_value=0.01, step=1.0)
        r = st.number_input("무위험이자율 (%)", value=5.0, min_value=0.0, max_value=100.0, step=0.1) / 100

    with col2:
        q = st.number_input("배당수익률 (%)", value=2.0, min_value=0.0, max_value=100.0, step=0.1) / 100
        T_days = st.number_input("만기 (일)", value=90, min_value=1, step=1)
        T = T_days / 365

    if st.button("💰 계산하기", type="primary"):
        try:
            futures = FuturesModel(S, r, q, T)
            theo_price = futures.theoretical_price()

            st.markdown("---")
            st.subheader("💰 계산 결과")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("현물 가격", f"${S:.2f}")
            with col2:
                st.metric("이론적 선물가격", f"${theo_price:.2f}")
            with col3:
                basis = theo_price - S
                st.metric("이론적 베이시스", f"${basis:.2f}")

            # 실제 선물 가격 입력
            st.markdown("---")
            st.subheader("📊 차익거래 분석")

            market_price = st.number_input("실제 선물 시장 가격 ($)", value=theo_price, step=0.1)
            transaction_cost = st.number_input("거래비용 (%)", value=0.1, step=0.01) / 100

            if st.button("차익거래 분석"):
                arb_analysis = futures.arbitrage_profit(market_price, transaction_cost)

                col1, col2 = st.columns(2)

                with col1:
                    st.metric("실제 시장가격", f"${arb_analysis['market_price']:.2f}")
                    st.metric("이론 가격과의 차이", f"${arb_analysis['price_difference']:.2f}")

                with col2:
                    st.metric("실제 베이시스", f"${futures.basis(market_price):.2f}")
                    if arb_analysis['arbitrage_opportunity']:
                        st.success("✅ 차익거래 기회 존재!")
                    else:
                        st.info("ℹ️ 차익거래 기회 없음")

        except Exception as e:
            st.error(f"계산 중 오류가 발생했습니다: {str(e)}")

# ===== Greeks 분석 =====
elif menu == "🎯 Greeks 분석":
    st.header("🎯 Greeks 민감도 분석")
    st.markdown("옵션 가격의 다양한 요인에 대한 민감도 분석")

    col1, col2 = st.columns(2)

    with col1:
        K = st.number_input("행사가격 ($)", value=100.0, min_value=0.01, step=1.0)
        T_days = st.number_input("만기 (일)", value=30, min_value=1, step=1)
        T = T_days / 365

    with col2:
        r = st.number_input("무위험이자율 (%)", value=5.0, min_value=0.0, step=0.1) / 100
        option_type = st.selectbox("옵션 타입", ["Call", "Put"])

    greek_type = st.selectbox(
        "분석할 Greek 선택",
        ["Delta", "Gamma", "Theta", "Vega"]
    )

    if st.button("📊 히트맵 생성", type="primary"):
        try:
            fig = create_greeks_heatmap(K, T, r, greek_type.lower(), option_type.lower())
            st.plotly_chart(fig, use_container_width=True)

            # Greek 설명
            st.markdown("---")
            st.subheader(f"📚 {greek_type} 설명")

            descriptions = {
                "Delta": """
                **Delta (Δ)**는 기초자산 가격이 $1 변할 때 옵션 가격의 변화를 나타냅니다.
                - 콜 옵션: 0 ~ 1 (양수)
                - 풋 옵션: -1 ~ 0 (음수)
                - ITM 옵션일수록 |Delta|가 1에 가까워집니다.
                """,
                "Gamma": """
                **Gamma (Γ)**는 기초자산 가격이 $1 변할 때 Delta의 변화를 나타냅니다.
                - 항상 양수
                - ATM 옵션에서 최대값
                - 만기가 가까울수록 증가
                """,
                "Theta": """
                **Theta (Θ)**는 하루가 지날 때 옵션 가격의 변화(시간 가치 감소)를 나타냅니다.
                - 일반적으로 음수
                - 만기가 가까울수록 절대값 증가
                - ATM 옵션에서 최대
                """,
                "Vega": """
                **Vega (ν)**는 변동성이 1% 변할 때 옵션 가격의 변화를 나타냅니다.
                - 항상 양수
                - ATM 옵션에서 최대
                - 만기가 길수록 증가
                """
            }

            st.info(descriptions[greek_type])

        except Exception as e:
            st.error(f"히트맵 생성 중 오류가 발생했습니다: {str(e)}")

# ===== 이론 설명 =====
elif menu == "📚 이론 설명":
    st.header("📚 파생상품 이론")

    tab1, tab2, tab3 = st.tabs(["옵션", "선물", "Black-Scholes 모델"])

    with tab1:
        st.subheader("옵션 (Options)")
        st.markdown("""
        옵션은 미래의 특정 시점에 특정 가격으로 자산을 사거나 팔 수 있는 **권리**입니다.

        ### 콜 옵션 (Call Option)
        - 기초자산을 **살 권리**
        - 손익: max(S - K, 0) - Premium
        - 기초자산 가격이 상승할 것으로 예상할 때 매수

        ### 풋 옵션 (Put Option)
        - 기초자산을 **팔 권리**
        - 손익: max(K - S, 0) - Premium
        - 기초자산 가격이 하락할 것으로 예상할 때 매수

        ### 주요 용어
        - **행사가격 (Strike Price, K)**: 옵션 행사 시 거래 가격
        - **만기 (Maturity, T)**: 옵션이 만료되는 날짜
        - **프리미엄 (Premium)**: 옵션 구매 비용
        - **내재가치 (Intrinsic Value)**: 즉시 행사 시 이익
        - **시간가치 (Time Value)**: 프리미엄 - 내재가치
        """)

    with tab2:
        st.subheader("선물 (Futures)")
        st.markdown("""
        선물은 미래의 특정 시점에 특정 가격으로 자산을 사거나 팔 **의무**가 있는 계약입니다.

        ### 특징
        - 표준화된 계약
        - 거래소에서 거래
        - 일일정산 (Mark-to-Market)
        - 증거금 요구

        ### 이론적 선물 가격
        F = S × e^((r - q) × T)

        여기서:
        - F: 선물 가격
        - S: 현물 가격
        - r: 무위험 이자율
        - q: 배당수익률
        - T: 만기

        ### 베이시스 (Basis)
        베이시스 = 선물 가격 - 현물 가격

        - 정상시장 (Contango): 베이시스 > 0
        - 역조시장 (Backwardation): 베이시스 < 0
        """)

    with tab3:
        st.subheader("Black-Scholes 모델")
        st.markdown("""
        Black-Scholes 모델은 유럽형 옵션의 이론적 가격을 계산하는 수학적 모델입니다.

        ### 가정
        1. 주가는 로그정규분포를 따름
        2. 변동성과 무위험이자율은 일정
        3. 거래비용과 세금이 없음
        4. 배당이 없음
        5. 차익거래 기회가 없음

        ### 콜 옵션 가격 공식
        C = S × N(d₁) - K × e^(-rT) × N(d₂)

        ### 풋 옵션 가격 공식
        P = K × e^(-rT) × N(-d₂) - S × N(-d₁)

        ### 변수
        - d₁ = [ln(S/K) + (r + σ²/2)T] / (σ√T)
        - d₂ = d₁ - σ√T
        - N(x): 표준정규분포 누적분포함수

        ### Greeks
        옵션 가격의 민감도 지표:
        - **Delta**: ∂C/∂S (가격 민감도)
        - **Gamma**: ∂²C/∂S² (Delta 변화율)
        - **Theta**: ∂C/∂t (시간 가치 감소)
        - **Vega**: ∂C/∂σ (변동성 민감도)
        - **Rho**: ∂C/∂r (이자율 민감도)
        """)

# 푸터
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    <p>📊 파생상품 시뮬레이션 대시보드 v1.0</p>
    <p>⚠️ 교육용 도구입니다. 실제 투자 결정에 사용하지 마세요.</p>
</div>
""", unsafe_allow_html=True)
