"""
리스크 관리 모듈

포트폴리오의 리스크를 측정하고 관리하는 기능을 제공합니다.
- VaR (Value at Risk)
- CVaR (Conditional VaR)
- 포트폴리오 최적화
- 상관관계 분석
"""

import numpy as np
from typing import Dict, List, Tuple
import pandas as pd


class VaRCalculator:
    """
    VaR (Value at Risk) 계산기
    
    포트폴리오가 특정 신뢰수준에서 일정 기간 내에 입을 수 있는
    최대 손실액을 계산합니다.
    """
    
    def __init__(self, returns: np.ndarray, confidence_level: float = 0.95):
        """
        Parameters
        ----------
        returns : np.ndarray
            수익률 시계열
        confidence_level : float
            신뢰수준 (0.95 = 95%)
        """
        self.returns = returns
        self.confidence_level = confidence_level
        self.alpha = 1 - confidence_level
    
    def historical_var(self, portfolio_value: float) -> float:
        """
        역사적 VaR 계산
        
        과거 수익률 분포에서 직접 VaR을 계산합니다.
        """
        var_percentile = np.percentile(self.returns, self.alpha * 100)
        var = portfolio_value * abs(var_percentile)
        return var
    
    def parametric_var(self, portfolio_value: float) -> float:
        """
        파라메트릭 VaR 계산 (정규분포 가정)
        
        수익률이 정규분포를 따른다고 가정합니다.
        """
        mean_return = np.mean(self.returns)
        std_return = np.std(self.returns)
        
        # Z-score (표준정규분포에서 신뢰수준에 해당하는 값)
        z_score = np.abs(np.percentile(np.random.randn(100000), self.alpha * 100))
        
        # VaR = 포트폴리오 가치 × (평균 - Z × 표준편차)
        var = portfolio_value * abs(mean_return - z_score * std_return)
        
        return var
    
    def conditional_var(self, portfolio_value: float) -> float:
        """
        CVaR (Conditional VaR) 또는 Expected Shortfall 계산
        
        VaR을 초과하는 손실의 평균값
        """
        var_percentile = np.percentile(self.returns, self.alpha * 100)
        cvar_return = self.returns[self.returns <= var_percentile].mean()
        cvar = portfolio_value * abs(cvar_return)
        
        return cvar


class PortfolioOptimizer:
    """
    포트폴리오 최적화
    
    주어진 자산들의 최적 배치를 찾습니다.
    """
    
    def __init__(self, returns: pd.DataFrame, cov_matrix: pd.DataFrame = None):
        """
        Parameters
        ----------
        returns : pd.DataFrame
            자산별 수익률
        cov_matrix : pd.DataFrame
            공분산 행렬
        """
        self.returns = returns
        self.mean_returns = returns.mean()
        
        if cov_matrix is None:
            self.cov_matrix = returns.cov()
        else:
            self.cov_matrix = cov_matrix
    
    def calculate_portfolio_stats(self, weights: np.ndarray) -> Tuple[float, float]:
        """
        포트폴리오 통계 계산
        
        Returns
        -------
        tuple
            (기대 수익률, 표준편차)
        """
        portfolio_return = np.sum(self.mean_returns * weights)
        portfolio_std = np.sqrt(np.dot(weights.T, np.dot(self.cov_matrix, weights)))
        
        return portfolio_return, portfolio_std
    
    def calculate_sharpe_ratio(self, weights: np.ndarray, risk_free_rate: float = 0.02) -> float:
        """
        샤프 비율 계산
        
        (포트폴리오 수익률 - 무위험이자율) / 표준편차
        """
        p_return, p_std = self.calculate_portfolio_stats(weights)
        sharpe = (p_return - risk_free_rate) / p_std if p_std > 0 else 0
        return sharpe
    
    def minimum_variance_portfolio(self) -> Dict:
        """
        최소 분산 포트폴리오 찾기
        """
        n_assets = len(self.mean_returns)
        
        # 제약 조건: weights 합 = 1, 모두 양수
        from scipy.optimize import minimize
        
        def portfolio_variance(weights):
            return np.dot(weights.T, np.dot(self.cov_matrix, weights))
        
        constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
        bounds = tuple((0, 1) for _ in range(n_assets))
        initial_weights = np.array([1/n_assets] * n_assets)
        
        result = minimize(
            portfolio_variance,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        weights = result.x
        p_return, p_std = self.calculate_portfolio_stats(weights)
        
        return {
            'weights': weights,
            'return': p_return,
            'std': p_std,
            'sharpe': self.calculate_sharpe_ratio(weights)
        }
    
    def maximum_sharpe_portfolio(self, risk_free_rate: float = 0.02) -> Dict:
        """
        샤프 비율 최대화 포트폴리오
        """
        n_assets = len(self.mean_returns)
        
        from scipy.optimize import minimize
        
        def neg_sharpe(weights):
            return -self.calculate_sharpe_ratio(weights, risk_free_rate)
        
        constraints = {'type': 'eq', 'fun': lambda x: np.sum(x) - 1}
        bounds = tuple((0, 1) for _ in range(n_assets))
        initial_weights = np.array([1/n_assets] * n_assets)
        
        result = minimize(
            neg_sharpe,
            initial_weights,
            method='SLSQP',
            bounds=bounds,
            constraints=constraints
        )
        
        weights = result.x
        p_return, p_std = self.calculate_portfolio_stats(weights)
        
        return {
            'weights': weights,
            'return': p_return,
            'std': p_std,
            'sharpe': self.calculate_sharpe_ratio(weights, risk_free_rate)
        }


class CorrelationAnalysis:
    """
    상관관계 분석
    
    자산 간의 상관관계를 분석합니다.
    """
    
    @staticmethod
    def rolling_correlation(series1: np.ndarray, series2: np.ndarray, 
                           window: int = 30) -> np.ndarray:
        """
        롤링 상관관계 계산
        
        Parameters
        ----------
        series1, series2 : np.ndarray
            두 자산의 시계열
        window : int
            계산 윈도우 (일)
        
        Returns
        -------
        np.ndarray
            시간에 따른 상관관계
        """
        correlations = []
        for i in range(len(series1) - window):
            corr = np.corrcoef(series1[i:i+window], series2[i:i+window])[0, 1]
            correlations.append(corr)
        
        return np.array(correlations)
    
    @staticmethod
    def correlation_matrix(returns: pd.DataFrame) -> pd.DataFrame:
        """
        상관관계 행렬 생성
        """
        return returns.corr()
    
    @staticmethod
    def diversification_ratio(weights: np.ndarray, 
                             individual_vols: np.ndarray,
                             portfolio_vol: float) -> float:
        """
        다각화 비율 계산
        
        (가중평균 개별 변동성) / (포트폴리오 변동성)
        높을수록 다각화가 잘됨
        """
        weighted_vol = np.sum(weights * individual_vols)
        return weighted_vol / portfolio_vol if portfolio_vol > 0 else 0


class RiskMetrics:
    """
    위험 지표 계산
    """
    
    @staticmethod
    def drawdown(prices: np.ndarray) -> np.ndarray:
        """
        드로우다운 계산 (최고점에서 현재까지 하락률)
        """
        running_max = np.maximum.accumulate(prices)
        drawdown = (prices - running_max) / running_max
        return np.abs(drawdown)
    
    @staticmethod
    def max_drawdown(prices: np.ndarray) -> float:
        """
        최대 드로우다운
        """
        return np.max(RiskMetrics.drawdown(prices))
    
    @staticmethod
    def sortino_ratio(returns: np.ndarray, target_return: float = 0.0,
                     risk_free_rate: float = 0.0) -> float:
        """
        소르티노 비율
        
        샤프 비율과 달리, 아래쪽 변동성만 고려합니다.
        """
        excess_returns = returns - target_return
        downside_returns = excess_returns[excess_returns < 0]
        downside_std = np.std(downside_returns)
        
        sortino = (np.mean(returns) - risk_free_rate) / downside_std if downside_std > 0 else 0
        return sortino
    
    @staticmethod
    def calmar_ratio(returns: np.ndarray, prices: np.ndarray) -> float:
        """
        칼마 비율 = 연간 수익률 / 최대 드로우다운
        """
        annual_return = np.mean(returns) * 252
        max_dd = RiskMetrics.max_drawdown(prices)
        
        return annual_return / max_dd if max_dd > 0 else 0


# 사용 예제
if __name__ == "__main__":
    print("="*70)
    print("리스크 관리 모듈 - 사용 예제")
    print("="*70)
    
    # 샘플 데이터 생성
    np.random.seed(42)
    returns = np.random.randn(252) * 0.02 + 0.0005
    prices = 100 * (1 + returns).cumprod()
    portfolio_value = 1000000
    
    # VaR 계산
    print("\n1. VaR 계산")
    print("-"*70)
    
    var_calc = VaRCalculator(returns, confidence_level=0.95)
    hist_var = var_calc.historical_var(portfolio_value)
    cvar = var_calc.conditional_var(portfolio_value)
    
    print(f"포트폴리오 가치: ${portfolio_value:,.0f}")
    print(f"역사적 VaR (95%): ${hist_var:,.0f}")
    print(f"CVaR (95%): ${cvar:,.0f}")
    
    # 최대 드로우다운
    print("\n2. 위험 지표")
    print("-"*70)
    
    max_dd = RiskMetrics.max_drawdown(prices)
    print(f"최대 드로우다운: {max_dd*100:.2f}%")
    
    # 샤프 비율
    sharpe = (np.mean(returns)*252 - 0.02) / (np.std(returns)*np.sqrt(252))
    print(f"샤프 비율: {sharpe:.2f}")
    
    # 칼마 비율
    calmar = RiskMetrics.calmar_ratio(returns, prices)
    print(f"칼마 비율: {calmar:.2f}")
