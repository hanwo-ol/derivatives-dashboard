"""
금융 계산 유틸리티 함수
"""

import numpy as np
from typing import List, Dict


def calculate_portfolio_value(positions: List[Dict]) -> float:
    """
    포트폴리오 총 가치 계산

    Parameters
    ----------
    positions : list of dict
        포지션 정보 리스트

    Returns
    -------
    float
        총 포트폴리오 가치
    """
    total = sum(pos.get('quantity', 0) * pos.get('price', 0) for pos in positions)
    return total


def calculate_historical_volatility(prices: np.ndarray, window: int = 30) -> float:
    """
    역사적 변동성 계산

    Parameters
    ----------
    prices : np.ndarray
        가격 시계열
    window : int
        계산 윈도우 (일)

    Returns
    -------
    float
        연율 변동성
    """
    if len(prices) < 2:
        return 0.0

    # 로그 수익률 계산
    returns = np.log(prices[1:] / prices[:-1])

    # 최근 window 개 데이터 사용
    recent_returns = returns[-window:] if len(returns) > window else returns

    # 일별 변동성
    daily_vol = np.std(recent_returns)

    # 연율 변동성 (252 거래일 가정)
    annual_vol = daily_vol * np.sqrt(252)

    return annual_vol


def calculate_sharpe_ratio(
    returns: np.ndarray,
    risk_free_rate: float = 0.02,
    periods_per_year: int = 252
) -> float:
    """
    샤프 비율 계산

    Parameters
    ----------
    returns : np.ndarray
        수익률 시계열
    risk_free_rate : float
        무위험이자율 (연율)
    periods_per_year : int
        연간 기간 수

    Returns
    -------
    float
        샤프 비율
    """
    if len(returns) == 0:
        return 0.0

    # 평균 수익률
    mean_return = np.mean(returns) * periods_per_year

    # 표준편차
    std_return = np.std(returns) * np.sqrt(periods_per_year)

    if std_return == 0:
        return 0.0

    # 샤프 비율
    sharpe = (mean_return - risk_free_rate) / std_return

    return sharpe


def calculate_var(
    returns: np.ndarray,
    confidence_level: float = 0.95
) -> float:
    """
    VaR (Value at Risk) 계산

    Parameters
    ----------
    returns : np.ndarray
        수익률 시계열
    confidence_level : float
        신뢰수준

    Returns
    -------
    float
        VaR 값
    """
    if len(returns) == 0:
        return 0.0

    var = np.percentile(returns, (1 - confidence_level) * 100)
    return abs(var)


if __name__ == "__main__":
    # 테스트
    print("계산 유틸리티 모듈 로드 완료")

    # 샘플 데이터
    prices = np.array([100, 102, 101, 103, 105, 104, 106, 108, 107, 109])
    vol = calculate_historical_volatility(prices)
    print(f"역사적 변동성: {vol*100:.2f}%")
