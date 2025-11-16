"""
헤지펀드 전략 시뮬레이터

이 모듈은 다양한 헤지펀드 전략을 시뮬레이션하고 분석합니다.
- Long/Short Equity: 롱/숏 전략
- Pairs Trading: 페어 트레이딩
- Market Neutral: 시장 중립 전략
- Leverage: 레버리지 효과 분석
"""

import numpy as np
from typing import Dict, List
import pandas as pd


class HedgeFundStrategy:
    """
    헤지펀드 전략 기본 클래스
    
    Parameters
    ----------
    initial_capital : float
        초기 자본금
    leverage_ratio : float
        레버리지 비율 (1.0 = 무레버리지, 2.0 = 2배 레버리지)
    borrowing_rate : float
        차입 이자율 (연율, 소수점)
    """
    
    def __init__(self, initial_capital: float, leverage_ratio: float = 1.0, 
                 borrowing_rate: float = 0.03):
        if initial_capital <= 0:
            raise ValueError("초기 자본금은 0보다 커야 합니다.")
        if leverage_ratio < 1.0:
            raise ValueError("레버리지는 1.0 이상이어야 합니다.")
        
        self.initial_capital = initial_capital
        self.leverage_ratio = leverage_ratio
        self.borrowing_rate = borrowing_rate
        self.borrowed_capital = initial_capital * (leverage_ratio - 1.0)
        self.total_capital = initial_capital * leverage_ratio
    
    def calculate_borrowing_cost(self, holding_days: int) -> float:
        """
        차입 비용 계산
        
        Parameters
        ----------
        holding_days : int
            보유 기간 (일)
        
        Returns
        -------
        float
            총 차입 비용
        """
        daily_rate = self.borrowing_rate / 365
        total_cost = self.borrowed_capital * daily_rate * holding_days
        return total_cost


class LongShortStrategy(HedgeFundStrategy):
    """
    롱/숏 전략
    
    롱 포지션 (매수)과 숏 포지션 (공매도)을 동시에 구성하는 전략
    """
    
    def __init__(self, initial_capital: float, leverage_ratio: float = 1.0,
                 borrowing_rate: float = 0.03, short_rebate_rate: float = 0.01):
        super().__init__(initial_capital, leverage_ratio, borrowing_rate)
        self.short_rebate_rate = short_rebate_rate
        self.long_holdings = {}
        self.short_holdings = {}
    
    def add_long_position(self, symbol: str, price: float, quantity: int):
        """롱 포지션 추가 - 기초자산 매수"""
        self.long_holdings[symbol] = {
            'entry_price': price,
            'quantity': quantity,
            'entry_value': price * quantity
        }
    
    def add_short_position(self, symbol: str, price: float, quantity: int):
        """숏 포지션 추가 - 기초자산 공매도"""
        self.short_holdings[symbol] = {
            'entry_price': price,
            'quantity': quantity,
            'entry_value': price * quantity
        }
    
    def calculate_positions_value(self, long_prices: Dict[str, float], 
                                 short_prices: Dict[str, float]) -> Dict:
        """
        현재 포지션 가치 계산
        
        Parameters
        ----------
        long_prices : dict
            {'symbol': current_price}
        short_prices : dict
            {'symbol': current_price}
        
        Returns
        -------
        dict
            현재 가치 및 손익 분석
        """
        # 롱 포지션 계산
        long_value = 0
        long_pnl = 0
        for symbol, holding in self.long_holdings.items():
            if symbol in long_prices:
                current_value = long_prices[symbol] * holding['quantity']
                pnl = current_value - holding['entry_value']
                long_value += current_value
                long_pnl += pnl
        
        # 숏 포지션 계산
        short_value = 0
        short_pnl = 0
        for symbol, holding in self.short_holdings.items():
            if symbol in short_prices:
                current_price = short_prices[symbol]
                # 숏 포지션: 진입 가격이 낮을수록 수익
                short_pnl += (holding['entry_price'] - current_price) * holding['quantity']
                short_value -= current_price * holding['quantity']
        
        net_value = long_value + short_value
        total_pnl = long_pnl + short_pnl
        
        return {
            'long_value': long_value,
            'short_value': short_value,
            'net_value': net_value,
            'long_pnl': long_pnl,
            'short_pnl': short_pnl,
            'total_pnl': total_pnl,
            'return': total_pnl / self.initial_capital if self.initial_capital > 0 else 0
        }
    
    def calculate_market_exposure(self) -> Dict:
        """
        시장 노출도 계산 (Market Exposure)
        
        시장 중립 전략이 얼마나 성공했는지 분석
        """
        long_value = sum(h['entry_value'] for h in self.long_holdings.values())
        short_value = sum(h['entry_value'] for h in self.short_holdings.values())
        
        gross_value = long_value + short_value
        net_value = long_value - short_value
        
        # 시장 중립도
        market_neutral = abs(net_value) / gross_value if gross_value > 0 else 0
        
        return {
            'long_exposure': long_value,
            'short_exposure': short_value,
            'gross_exposure': gross_value,
            'net_exposure': net_value,
            'market_neutral_ratio': market_neutral,
            'is_market_neutral': market_neutral < 0.1
        }


class PairsTrading(HedgeFundStrategy):
    """
    페어 트레이딩 전략
    
    상관관계 높은 두 자산을 동시에 거래하는 전략
    (하나는 롱, 하나는 숏)
    """
    
    def __init__(self, initial_capital: float, correlation_threshold: float = 0.8):
        super().__init__(initial_capital)
        self.correlation_threshold = correlation_threshold
        self.pairs = []
    
    def add_pair(self, symbol_long: str, symbol_short: str, correlation: float):
        """페어 추가"""
        if correlation < self.correlation_threshold:
            print(f"경고: 상관관계 {correlation:.2f}가 임계값 {self.correlation_threshold}보다 낮습니다.")
        
        self.pairs.append({
            'long': symbol_long,
            'short': symbol_short,
            'correlation': correlation
        })
    
    def calculate_spread(self, long_price: float, short_price: float,
                        historical_mean: float, historical_std: float) -> Dict:
        """
        스프레드 계산
        
        Z-Score를 통해 평균 회귀 기회를 찾음
        Z = (현재값 - 평균) / 표준편차
        """
        current_spread = long_price - short_price
        z_score = (current_spread - historical_mean) / historical_std if historical_std > 0 else 0
        
        return {
            'current_spread': current_spread,
            'historical_mean': historical_mean,
            'z_score': z_score,
            'is_overvalued': z_score > 2,
            'is_undervalued': z_score < -2,
            'mean_reversion_opportunity': abs(z_score) > 2
        }


class Leverage:
    """
    레버리지 계산 및 시뮬레이션
    
    레버리지의 영향을 분석하는 도구
    """
    
    @staticmethod
    def calculate_leveraged_return(unleveraged_return: float, leverage_ratio: float,
                                  borrowing_rate: float, holding_days: int) -> float:
        """
        레버리지 수익률 계산
        
        Parameters
        ----------
        unleveraged_return : float
            레버리지 없는 수익률
        leverage_ratio : float
            레버리지 배율
        borrowing_rate : float
            차입 이자율 (연율)
        holding_days : int
            보유 기간 (일)
        
        Returns
        -------
        float
            레버리지 적용 후 수익률
        """
        # 차입 이자 비용
        daily_rate = borrowing_rate / 365
        borrowed_portion = leverage_ratio - 1.0
        borrowing_cost = borrowed_portion * daily_rate * holding_days
        
        # 레버리지 수익 = 언레버리지 수익 × 레버리지 - 차입 비용
        leveraged_return = unleveraged_return * leverage_ratio - borrowing_cost
        
        return leveraged_return
    
    @staticmethod
    def margin_call_price(entry_price: float, leverage_ratio: float,
                         margin_requirement: float = 0.30) -> float:
        """
        마진 콜 가격 계산
        
        Parameters
        ----------
        entry_price : float
            진입 가격
        leverage_ratio : float
            레버리지 배율
        margin_requirement : float
            유지 마진율 (기본값 30%)
        
        Returns
        -------
        float
            마진 콜이 발생하는 가격
        """
        max_loss = 1 - margin_requirement
        price_decline_pct = max_loss / leverage_ratio
        margin_call_price = entry_price * (1 - price_decline_pct)
        
        return margin_call_price
    
    @staticmethod
    def leverage_scenarios(initial_investment: float, price_change_pct: float,
                          leverage_ratios: List[float],
                          borrowing_rate: float = 0.03,
                          holding_days: int = 30):
        """
        여러 레버리지 시나리오 분석
        
        Returns
        -------
        pd.DataFrame
            다양한 레버리지 배율에 따른 수익률 비교
        """
        scenarios = []
        
        for leverage in leverage_ratios:
            borrowed_amount = initial_investment * (leverage - 1)
            borrowing_cost = borrowed_amount * borrowing_rate / 365 * holding_days
            
            gross_profit = initial_investment * leverage * price_change_pct
            net_profit = gross_profit - borrowing_cost
            net_return = net_profit / initial_investment
            
            scenarios.append({
                'leverage': leverage,
                'gross_profit': gross_profit,
                'borrowing_cost': borrowing_cost,
                'net_profit': net_profit,
                'net_return': net_return
            })
        
        return pd.DataFrame(scenarios)


# 사용 예제
if __name__ == "__main__":
    print("="*70)
    print("헤지펀드 전략 시뮬레이터")
    print("="*70)
    
    # Long/Short 전략 예제
    print("\n1. Long/Short 전략 예제")
    print("-"*70)
    
    ls_strategy = LongShortStrategy(
        initial_capital=1000000,
        leverage_ratio=2.0,
        borrowing_rate=0.03
    )
    
    # 롱 포지션: Apple 1000주 @ $150
    ls_strategy.add_long_position('AAPL', 150.0, 1000)
    
    # 숏 포지션: Microsoft 500주 @ $300 (공매도)
    ls_strategy.add_short_position('MSFT', 300.0, 500)
    
    # 현재 가격
    current_prices_long = {'AAPL': 155.0}
    current_prices_short = {'MSFT': 295.0}
    
    result = ls_strategy.calculate_positions_value(current_prices_long, current_prices_short)
    print(f"\n포트폴리오 가치:")
    print(f"  롱 포지션 손익: ${result['long_pnl']:,.2f}")
    print(f"  숏 포지션 손익: ${result['short_pnl']:,.2f}")
    print(f"  총 손익: ${result['total_pnl']:,.2f}")
    print(f"  수익률: {result['return']*100:.2f}%")
    
    # 시장 노출도
    exposure = ls_strategy.calculate_market_exposure()
    print(f"\n시장 노출도:")
    print(f"  총 노출도: ${exposure['gross_exposure']:,.0f}")
    print(f"  순 노출도: ${exposure['net_exposure']:,.0f}")
    print(f"  시장중립도: {(1-exposure['market_neutral_ratio'])*100:.1f}%")
    
    # 레버리지 시나리오
    print("\n\n2. 레버리지 시나리오 분석 (+5% 수익률)")
    print("-"*70)
    
    scenarios = Leverage.leverage_scenarios(
        initial_investment=1000000,
        price_change_pct=0.05,
        leverage_ratios=[1.0, 2.0, 3.0, 5.0],
        borrowing_rate=0.03,
        holding_days=30
    )
    
    print("\n수익률 비교:")
    for _, row in scenarios.iterrows():
        print(f"  {row['leverage']:.1f}x 레버리지: "
              f"수익 ${row['net_profit']:,.0f}, 수익률 {row['net_return']*100:.2f}%")
    
    # 마진 콜 분석
    print("\n\n3. 마진 콜 분석")
    print("-"*70)
    
    entry_price = 100.0
    leverage = 3.0
    margin_call = Leverage.margin_call_price(entry_price, leverage)
    
    print(f"\n진입 가격: ${entry_price:.2f}")
    print(f"레버리지: {leverage}x")
    print(f"마진 콜 가격: ${margin_call:.2f} (하락폭: {(entry_price - margin_call)/entry_price*100:.1f}%)")
