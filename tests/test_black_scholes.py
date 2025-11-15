"""
Black-Scholes 모델 테스트
"""

import pytest
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from models.black_scholes import BlackScholesModel, calculate_implied_volatility


class TestBlackScholesModel:
    """Black-Scholes 모델 테스트"""

    def test_initialization(self):
        """초기화 테스트"""
        bs = BlackScholesModel(S=100, K=100, T=1, r=0.05, sigma=0.2)
        assert bs.S == 100
        assert bs.K == 100
        assert bs.T == 1
        assert bs.r == 0.05
        assert bs.sigma == 0.2

    def test_invalid_parameters(self):
        """잘못된 파라미터 테스트"""
        with pytest.raises(ValueError):
            BlackScholesModel(S=-100, K=100, T=1, r=0.05, sigma=0.2)

        with pytest.raises(ValueError):
            BlackScholesModel(S=100, K=-100, T=1, r=0.05, sigma=0.2)

        with pytest.raises(ValueError):
            BlackScholesModel(S=100, K=100, T=-1, r=0.05, sigma=0.2)

        with pytest.raises(ValueError):
            BlackScholesModel(S=100, K=100, T=1, r=0.05, sigma=-0.2)

    def test_call_price(self):
        """콜 옵션 가격 테스트"""
        bs = BlackScholesModel(S=100, K=100, T=1, r=0.05, sigma=0.2)
        call_price = bs.call_price()

        assert call_price > 0
        assert isinstance(call_price, float)
        # ATM 옵션이므로 합리적인 범위 내
        assert 5 < call_price < 15

    def test_put_price(self):
        """풋 옵션 가격 테스트"""
        bs = BlackScholesModel(S=100, K=100, T=1, r=0.05, sigma=0.2)
        put_price = bs.put_price()

        assert put_price > 0
        assert isinstance(put_price, float)
        assert 5 < put_price < 15

    def test_put_call_parity(self):
        """풋-콜 패리티 테스트"""
        S, K, T, r, sigma = 100, 100, 1, 0.05, 0.2
        bs = BlackScholesModel(S, K, T, r, sigma)

        call_price = bs.call_price()
        put_price = bs.put_price()

        # Put-Call Parity: C - P = S - K*e^(-rT)
        lhs = call_price - put_price
        rhs = S - K * np.exp(-r * T)

        assert abs(lhs - rhs) < 0.01

    def test_greeks_range(self):
        """Greeks 범위 테스트"""
        bs = BlackScholesModel(S=100, K=100, T=1, r=0.05, sigma=0.2)

        # Delta
        call_delta = bs.call_delta()
        put_delta = bs.put_delta()
        assert 0 <= call_delta <= 1
        assert -1 <= put_delta <= 0

        # Gamma
        gamma = bs.gamma()
        assert gamma > 0

        # Vega
        vega = bs.vega()
        assert vega > 0

    def test_intrinsic_value(self):
        """내재가치 테스트"""
        # ITM Call
        bs = BlackScholesModel(S=110, K=100, T=1, r=0.05, sigma=0.2)
        assert bs.intrinsic_value('call') == 10

        # OTM Call
        bs = BlackScholesModel(S=90, K=100, T=1, r=0.05, sigma=0.2)
        assert bs.intrinsic_value('call') == 0

        # ITM Put
        bs = BlackScholesModel(S=90, K=100, T=1, r=0.05, sigma=0.2)
        assert bs.intrinsic_value('put') == 10

    def test_time_value(self):
        """시간가치 테스트"""
        bs = BlackScholesModel(S=100, K=100, T=1, r=0.05, sigma=0.2)

        call_time_value = bs.time_value('call')
        put_time_value = bs.time_value('put')

        # ATM 옵션은 시간가치만 존재
        assert call_time_value > 0
        assert put_time_value > 0


class TestImpliedVolatility:
    """내재 변동성 계산 테스트"""

    def test_implied_volatility(self):
        """내재 변동성 계산 테스트"""
        S, K, T, r, sigma_true = 100, 100, 1, 0.05, 0.25

        # 실제 옵션 가격 계산
        bs = BlackScholesModel(S, K, T, r, sigma_true)
        market_price = bs.call_price()

        # 내재 변동성 역산
        sigma_implied = calculate_implied_volatility(
            market_price, S, K, T, r, 'call'
        )

        # 원래 변동성과 비슷해야 함
        assert abs(sigma_implied - sigma_true) < 0.01


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
