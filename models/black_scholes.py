"""
Black-Scholes 옵션 가격 계산 모델

이 모듈은 Black-Scholes-Merton 모델을 사용하여 유럽형 옵션의 가격과 Greeks를 계산합니다.
"""

import numpy as np
from scipy.stats import norm
from typing import Dict, Tuple


class BlackScholesModel:
    """
    Black-Scholes 옵션 가격 계산 모델

    Parameters
    ----------
    S : float
        기초자산의 현재 가격
    K : float
        행사가격 (Strike Price)
    T : float
        만기까지의 시간 (년 단위)
    r : float
        무위험 이자율 (연율, 소수점 형태: 0.05 = 5%)
    sigma : float
        변동성 (연율, 소수점 형태: 0.20 = 20%)

    Examples
    --------
    >>> bs = BlackScholesModel(S=100, K=105, T=30/365, r=0.05, sigma=0.20)
    >>> call_price = bs.call_price()
    >>> put_price = bs.put_price()
    >>> print(f"Call: ${call_price:.2f}, Put: ${put_price:.2f}")
    """

    def __init__(self, S: float, K: float, T: float, r: float, sigma: float):
        if S <= 0:
            raise ValueError("기초자산 가격(S)은 0보다 커야 합니다.")
        if K <= 0:
            raise ValueError("행사가격(K)은 0보다 커야 합니다.")
        if T <= 0:
            raise ValueError("만기(T)는 0보다 커야 합니다.")
        if sigma <= 0:
            raise ValueError("변동성(sigma)은 0보다 커야 합니다.")

        self.S = S
        self.K = K
        self.T = T
        self.r = r
        self.sigma = sigma

    def d1(self) -> float:
        """Black-Scholes d1 계산"""
        numerator = np.log(self.S / self.K) + (self.r + 0.5 * self.sigma**2) * self.T
        denominator = self.sigma * np.sqrt(self.T)
        return numerator / denominator

    def d2(self) -> float:
        """Black-Scholes d2 계산"""
        return self.d1() - self.sigma * np.sqrt(self.T)

    def call_price(self) -> float:
        """
        콜 옵션 가격 계산

        Returns
        -------
        float
            콜 옵션의 이론적 가격
        """
        d1 = self.d1()
        d2 = self.d2()
        price = self.S * norm.cdf(d1) - self.K * np.exp(-self.r * self.T) * norm.cdf(d2)
        return price

    def put_price(self) -> float:
        """
        풋 옵션 가격 계산

        Returns
        -------
        float
            풋 옵션의 이론적 가격
        """
        d1 = self.d1()
        d2 = self.d2()
        price = self.K * np.exp(-self.r * self.T) * norm.cdf(-d2) - self.S * norm.cdf(-d1)
        return price

    def call_delta(self) -> float:
        """콜 옵션 Delta (기초자산 가격 민감도)"""
        return norm.cdf(self.d1())

    def put_delta(self) -> float:
        """풋 옵션 Delta"""
        return norm.cdf(self.d1()) - 1

    def gamma(self) -> float:
        """
        Gamma (Delta의 변화율)

        콜과 풋 모두 동일한 Gamma 값을 가집니다.
        """
        d1 = self.d1()
        return norm.pdf(d1) / (self.S * self.sigma * np.sqrt(self.T))

    def vega(self) -> float:
        """
        Vega (변동성 민감도)

        1% 변동성 변화 시 옵션 가격 변화 (0.01 단위)
        """
        d1 = self.d1()
        return self.S * norm.pdf(d1) * np.sqrt(self.T) / 100

    def call_theta(self) -> float:
        """
        콜 옵션 Theta (시간 가치 감소)

        연간 단위이므로, 일일 Theta는 이 값을 365로 나눕니다.
        """
        d1 = self.d1()
        d2 = self.d2()
        term1 = -(self.S * norm.pdf(d1) * self.sigma) / (2 * np.sqrt(self.T))
        term2 = -self.r * self.K * np.exp(-self.r * self.T) * norm.cdf(d2)
        return term1 + term2

    def put_theta(self) -> float:
        """풋 옵션 Theta"""
        d1 = self.d1()
        d2 = self.d2()
        term1 = -(self.S * norm.pdf(d1) * self.sigma) / (2 * np.sqrt(self.T))
        term2 = self.r * self.K * np.exp(-self.r * self.T) * norm.cdf(-d2)
        return term1 + term2

    def call_rho(self) -> float:
        """
        콜 옵션 Rho (이자율 민감도)

        1% 이자율 변화 시 옵션 가격 변화 (0.01 단위)
        """
        d2 = self.d2()
        return self.K * self.T * np.exp(-self.r * self.T) * norm.cdf(d2) / 100

    def put_rho(self) -> float:
        """풋 옵션 Rho"""
        d2 = self.d2()
        return -self.K * self.T * np.exp(-self.r * self.T) * norm.cdf(-d2) / 100

    def get_all_greeks(self, option_type: str = 'call') -> Dict[str, float]:
        """
        모든 Greeks를 딕셔너리로 반환

        Parameters
        ----------
        option_type : str
            'call' 또는 'put'

        Returns
        -------
        dict
            모든 Greeks 값
        """
        if option_type.lower() == 'call':
            return {
                'delta': self.call_delta(),
                'gamma': self.gamma(),
                'theta': self.call_theta(),
                'theta_daily': self.call_theta() / 365,
                'vega': self.vega(),
                'rho': self.call_rho()
            }
        else:
            return {
                'delta': self.put_delta(),
                'gamma': self.gamma(),
                'theta': self.put_theta(),
                'theta_daily': self.put_theta() / 365,
                'vega': self.vega(),
                'rho': self.put_rho()
            }

    def intrinsic_value(self, option_type: str = 'call') -> float:
        """
        내재가치 계산

        Parameters
        ----------
        option_type : str
            'call' 또는 'put'

        Returns
        -------
        float
            옵션의 내재가치
        """
        if option_type.lower() == 'call':
            return max(0, self.S - self.K)
        else:
            return max(0, self.K - self.S)

    def time_value(self, option_type: str = 'call') -> float:
        """
        시간가치 계산 (옵션 가격 - 내재가치)

        Parameters
        ----------
        option_type : str
            'call' 또는 'put'

        Returns
        -------
        float
            옵션의 시간가치
        """
        if option_type.lower() == 'call':
            return self.call_price() - self.intrinsic_value('call')
        else:
            return self.put_price() - self.intrinsic_value('put')

    def __repr__(self) -> str:
        return (f"BlackScholesModel(S={self.S}, K={self.K}, T={self.T}, "
                f"r={self.r}, sigma={self.sigma})")


def calculate_implied_volatility(
    market_price: float,
    S: float,
    K: float,
    T: float,
    r: float,
    option_type: str = 'call',
    initial_sigma: float = 0.20,
    max_iterations: int = 100,
    tolerance: float = 1e-5
) -> float:
    """
    뉴턴-랩슨 방법을 사용한 내재 변동성 계산

    Parameters
    ----------
    market_price : float
        시장에서 관찰된 옵션 가격
    S, K, T, r : float
        Black-Scholes 파라미터
    option_type : str
        'call' 또는 'put'
    initial_sigma : float
        초기 변동성 추정값
    max_iterations : int
        최대 반복 횟수
    tolerance : float
        수렴 기준

    Returns
    -------
    float
        계산된 내재 변동성

    Raises
    ------
    ValueError
        수렴하지 않는 경우
    """
    sigma = initial_sigma

    for i in range(max_iterations):
        bs = BlackScholesModel(S, K, T, r, sigma)

        if option_type.lower() == 'call':
            price = bs.call_price()
        else:
            price = bs.put_price()

        vega = bs.vega() * 100  # vega를 실제 단위로 변환

        price_diff = price - market_price

        if abs(price_diff) < tolerance:
            return sigma

        if vega < 1e-10:
            raise ValueError("Vega가 너무 작아 계산할 수 없습니다.")

        sigma = sigma - price_diff / vega

        # 변동성이 음수가 되지 않도록
        sigma = max(sigma, 0.0001)

    raise ValueError(f"내재 변동성이 {max_iterations}회 반복 후에도 수렴하지 않았습니다.")


if __name__ == "__main__":
    # 사용 예제
    print("=" * 70)
    print("Black-Scholes 옵션 가격 계산 예제")
    print("=" * 70)

    # 파라미터 설정
    S = 100.0  # 기초자산 가격
    K = 105.0  # 행사가격
    T = 30/365  # 만기 (30일)
    r = 0.05  # 무위험이자율 5%
    sigma = 0.20  # 변동성 20%

    bs = BlackScholesModel(S, K, T, r, sigma)

    print(f"\n입력 파라미터:")
    print(f"  기초자산 가격 (S): ${S:.2f}")
    print(f"  행사가격 (K): ${K:.2f}")
    print(f"  만기 (T): 30일 ({T:.4f}년)")
    print(f"  무위험이자율 (r): {r*100:.1f}%")
    print(f"  변동성 (σ): {sigma*100:.1f}%")

    print(f"\n옵션 가격:")
    print(f"  콜 옵션: ${bs.call_price():.4f}")
    print(f"  풋 옵션: ${bs.put_price():.4f}")

    print(f"\nGreeks (Call):")
    greeks = bs.get_all_greeks('call')
    for greek_name, value in greeks.items():
        print(f"  {greek_name.capitalize()}: {value:.4f}")

    print(f"\n가치 분해 (Call):")
    print(f"  내재가치: ${bs.intrinsic_value('call'):.4f}")
    print(f"  시간가치: ${bs.time_value('call'):.4f}")
