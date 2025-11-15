"""
선물 가격 계산 모델

이 모듈은 이론적 선물 가격과 베이시스를 계산합니다.
"""

import numpy as np
from typing import Dict


class FuturesModel:
    """
    선물 가격 계산 모델

    Parameters
    ----------
    S : float
        현물 가격
    r : float
        무위험 이자율 (연율, 소수점)
    q : float
        배당수익률 또는 편의수익률 (연율, 소수점)
    T : float
        만기까지의 시간 (년)

    Examples
    --------
    >>> futures = FuturesModel(S=100, r=0.05, q=0.02, T=90/365)
    >>> theo_price = futures.theoretical_price()
    >>> print(f"이론적 선물가격: ${theo_price:.2f}")
    """

    def __init__(self, S: float, r: float, q: float = 0.0, T: float = 0.25):
        if S <= 0:
            raise ValueError("현물 가격(S)은 0보다 커야 합니다.")
        if T <= 0:
            raise ValueError("만기(T)는 0보다 커야 합니다.")

        self.S = S
        self.r = r
        self.q = q
        self.T = T

    def theoretical_price(self) -> float:
        """
        이론적 선물 가격 계산

        F = S * exp((r - q) * T)

        Returns
        -------
        float
            이론적 선물 가격
        """
        return self.S * np.exp((self.r - self.q) * self.T)

    def basis(self, futures_price: float) -> float:
        """
        베이시스 계산 (선물가격 - 현물가격)

        Parameters
        ----------
        futures_price : float
            실제 선물 시장 가격

        Returns
        -------
        float
            베이시스
        """
        return futures_price - self.S

    def arbitrage_profit(self, futures_price: float, transaction_cost: float = 0.0) -> Dict[str, float]:
        """
        차익거래 기회 분석

        Parameters
        ----------
        futures_price : float
            실제 선물 시장 가격
        transaction_cost : float
            거래비용 (%, 소수점)

        Returns
        -------
        dict
            차익거래 분석 결과
        """
        theo_price = self.theoretical_price()
        price_diff = futures_price - theo_price

        # 거래비용 고려
        buy_spot_sell_futures = price_diff - (self.S * transaction_cost)
        sell_spot_buy_futures = -price_diff - (self.S * transaction_cost)

        result = {
            'theoretical_price': theo_price,
            'market_price': futures_price,
            'price_difference': price_diff,
            'buy_spot_sell_futures_profit': buy_spot_sell_futures,
            'sell_spot_buy_futures_profit': sell_spot_buy_futures,
            'arbitrage_opportunity': abs(price_diff) > (self.S * transaction_cost)
        }

        return result

    def hedge_ratio(self, portfolio_beta: float = 1.0) -> float:
        """
        헷지 비율 계산

        Parameters
        ----------
        portfolio_beta : float
            포트폴리오 베타

        Returns
        -------
        float
            필요한 선물 계약 수
        """
        return portfolio_beta

    def __repr__(self) -> str:
        return f"FuturesModel(S={self.S}, r={self.r}, q={self.q}, T={self.T})"


if __name__ == "__main__":
    # 사용 예제
    print("=" * 70)
    print("선물 가격 계산 예제")
    print("=" * 70)

    S = 100.0  # 현물 가격
    r = 0.05  # 무위험이자율 5%
    q = 0.02  # 배당수익률 2%
    T = 90/365  # 만기 90일

    futures = FuturesModel(S, r, q, T)

    print(f"\n입력 파라미터:")
    print(f"  현물 가격: ${S:.2f}")
    print(f"  무위험이자율: {r*100:.1f}%")
    print(f"  배당수익률: {q*100:.1f}%")
    print(f"  만기: 90일 ({T:.4f}년)")

    theo_price = futures.theoretical_price()
    print(f"\n이론적 선물가격: ${theo_price:.2f}")

    # 실제 시장 가격 (예시)
    market_price = 100.75
    basis = futures.basis(market_price)
    print(f"\n실제 선물가격: ${market_price:.2f}")
    print(f"베이시스: ${basis:.2f}")

    # 차익거래 분석
    arb_analysis = futures.arbitrage_profit(market_price, transaction_cost=0.001)
    print(f"\n차익거래 분석:")
    for key, value in arb_analysis.items():
        if isinstance(value, bool):
            print(f"  {key}: {value}")
        else:
            print(f"  {key}: {value:.4f}")
