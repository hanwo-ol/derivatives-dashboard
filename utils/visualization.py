"""
시각화 함수

옵션 손익 다이어그램, Greeks 히트맵 등의 시각화 함수를 제공합니다.
"""

import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import List, Tuple, Optional
import sys
import os

# models 모듈 import를 위한 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.black_scholes import BlackScholesModel


def create_payoff_diagram(
    S: float,
    K: float,
    premium: float,
    option_type: str = 'call',
    option_position: str = 'long',
    price_range_pct: float = 0.4
) -> go.Figure:
    """
    옵션 손익 다이어그램 생성

    Parameters
    ----------
    S : float
        기초자산 현재 가격
    K : float
        행사가격
    premium : float
        옵션 프리미엄
    option_type : str
        'call' 또는 'put'
    option_position : str
        'long' 또는 'short'
    price_range_pct : float
        가격 범위 (행사가격 대비 %)

    Returns
    -------
    plotly.graph_objects.Figure
        손익 다이어그램
    """
    # 가격 범위 생성
    price_min = K * (1 - price_range_pct)
    price_max = K * (1 + price_range_pct)
    price_range = np.linspace(price_min, price_max, 200)

    # 손익 계산
    if option_type.lower() == 'call':
        if option_position.lower() == 'long':
            payoff = np.maximum(price_range - K, 0) - premium
            title = f"롱 콜 옵션 손익 (K=${K:.2f}, Premium=${premium:.2f})"
        else:  # short
            payoff = premium - np.maximum(price_range - K, 0)
            title = f"숏 콜 옵션 손익 (K=${K:.2f}, Premium=${premium:.2f})"
    else:  # put
        if option_position.lower() == 'long':
            payoff = np.maximum(K - price_range, 0) - premium
            title = f"롱 풋 옵션 손익 (K=${K:.2f}, Premium=${premium:.2f})"
        else:  # short
            payoff = premium - np.maximum(K - price_range, 0)
            title = f"숏 풋 옵션 손익 (K=${K:.2f}, Premium=${premium:.2f})"

    # Plotly 차트 생성
    fig = go.Figure()

    # 손익 곡선
    fig.add_trace(go.Scatter(
        x=price_range,
        y=payoff,
        mode='lines',
        name='손익',
        line=dict(color='blue', width=3),
        hovertemplate='기초자산 가격: $%{x:.2f}<br>손익: $%{y:.2f}<extra></extra>'
    ))

    # 손익분기점 표시
    fig.add_hline(y=0, line_dash="dash", line_color="red", 
                  annotation_text="손익분기", annotation_position="right")

    # 행사가격 표시
    fig.add_vline(x=K, line_dash="dash", line_color="green", 
                  annotation_text=f"행사가격 ${K:.2f}", annotation_position="top")

    # 현재가격 표시
    fig.add_vline(x=S, line_dash="dot", line_color="purple", 
                  annotation_text=f"현재가격 ${S:.2f}", annotation_position="bottom")

    # 레이아웃 설정
    fig.update_layout(
        title=title,
        xaxis_title="기초자산 가격 ($)",
        yaxis_title="손익 ($)",
        hovermode='x unified',
        showlegend=True,
        height=500,
        template='plotly_white'
    )

    return fig


def create_greeks_heatmap(
    K: float = 100,
    T: float = 30/365,
    r: float = 0.05,
    greek_type: str = 'delta',
    option_type: str = 'call'
) -> go.Figure:
    """
    Greeks 민감도 히트맵 생성

    Parameters
    ----------
    K : float
        행사가격
    T : float
        만기
    r : float
        무위험이자율
    greek_type : str
        'delta', 'gamma', 'theta', 'vega'
    option_type : str
        'call' 또는 'put'

    Returns
    -------
    plotly.graph_objects.Figure
        Greeks 히트맵
    """
    # 기초자산 가격 범위 (80-120)
    S_range = np.linspace(K * 0.8, K * 1.2, 30)

    # 변동성 범위 (10%-40%)
    sigma_range = np.linspace(0.10, 0.40, 30)

    # Greeks 계산
    greek_values = np.zeros((len(sigma_range), len(S_range)))

    for i, sigma in enumerate(sigma_range):
        for j, S in enumerate(S_range):
            try:
                bs = BlackScholesModel(S, K, T, r, sigma)

                if greek_type.lower() == 'delta':
                    value = bs.call_delta() if option_type == 'call' else bs.put_delta()
                elif greek_type.lower() == 'gamma':
                    value = bs.gamma()
                elif greek_type.lower() == 'theta':
                    value = bs.call_theta() / 365 if option_type == 'call' else bs.put_theta() / 365
                elif greek_type.lower() == 'vega':
                    value = bs.vega()
                else:
                    value = 0

                greek_values[i, j] = value
            except:
                greek_values[i, j] = np.nan

    # 히트맵 생성
    fig = go.Figure(data=go.Heatmap(
        z=greek_values,
        x=S_range,
        y=sigma_range * 100,  # % 단위로 변환
        colorscale='RdYlBu',
        hovertemplate='기초자산 가격: $%{x:.2f}<br>변동성: %{y:.1f}%<br>값: %{z:.4f}<extra></extra>'
    ))

    fig.update_layout(
        title=f'{greek_type.upper()} 민감도 분석 ({option_type.capitalize()} 옵션)',
        xaxis_title='기초자산 가격 ($)',
        yaxis_title='변동성 (%)',
        height=500,
        template='plotly_white'
    )

    return fig


def create_multi_strategy_payoff(
    strategies: List[dict],
    S_current: float,
    price_range_pct: float = 0.4
) -> go.Figure:
    """
    여러 옵션 전략의 손익을 한 차트에 표시

    Parameters
    ----------
    strategies : list of dict
        각 전략의 정보 [{'type': 'call', 'position': 'long', 'K': 100, 'premium': 5}, ...]
    S_current : float
        현재 기초자산 가격
    price_range_pct : float
        가격 범위

    Returns
    -------
    plotly.graph_objects.Figure
        복합 전략 손익 다이어그램
    """
    if not strategies:
        raise ValueError("최소 하나 이상의 전략이 필요합니다.")

    # 가격 범위 결정
    K_values = [s['K'] for s in strategies]
    K_avg = np.mean(K_values)
    price_min = K_avg * (1 - price_range_pct)
    price_max = K_avg * (1 + price_range_pct)
    price_range = np.linspace(price_min, price_max, 200)

    fig = go.Figure()

    total_payoff = np.zeros_like(price_range)

    # 각 전략의 손익 계산
    for strategy in strategies:
        option_type = strategy['type']
        position = strategy['position']
        K = strategy['K']
        premium = strategy['premium']

        if option_type.lower() == 'call':
            if position.lower() == 'long':
                payoff = np.maximum(price_range - K, 0) - premium
            else:
                payoff = premium - np.maximum(price_range - K, 0)
        else:  # put
            if position.lower() == 'long':
                payoff = np.maximum(K - price_range, 0) - premium
            else:
                payoff = premium - np.maximum(K - price_range, 0)

        total_payoff += payoff

        # 개별 전략 표시
        fig.add_trace(go.Scatter(
            x=price_range,
            y=payoff,
            mode='lines',
            name=f"{position.capitalize()} {option_type.capitalize()} K=${K}",
            line=dict(width=1, dash='dot'),
            opacity=0.5
        ))

    # 총 손익 표시
    fig.add_trace(go.Scatter(
        x=price_range,
        y=total_payoff,
        mode='lines',
        name='총 손익',
        line=dict(color='black', width=3)
    ))

    # 손익분기점 표시
    fig.add_hline(y=0, line_dash="dash", line_color="red")

    fig.update_layout(
        title="복합 옵션 전략 손익",
        xaxis_title="기초자산 가격 ($)",
        yaxis_title="손익 ($)",
        hovermode='x unified',
        height=500,
        template='plotly_white'
    )

    return fig


if __name__ == "__main__":
    # 테스트 코드
    print("시각화 모듈 로드 완료")

    # 손익 다이어그램 테스트
    fig1 = create_payoff_diagram(S=100, K=105, premium=2, option_type='call', option_position='long')
    print("✓ 손익 다이어그램 생성 완료")

    # Greeks 히트맵 테스트
    fig2 = create_greeks_heatmap(K=100, greek_type='delta', option_type='call')
    print("✓ Greeks 히트맵 생성 완료")
