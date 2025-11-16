"""
사모펀드 (Private Equity) 투자 분석

LBO (Leveraged Buyout) 모델링 및 사모펀드 수익률 분석
- 기업가치 평가 (DCF)
- 레버리지 구조 설계
- IRR 및 Multiple 계산
- 현금흐름 분석
"""

import numpy as np
from typing import Dict, List
import pandas as pd


class DCFValuation:
    """
    현금흐름 할인(DCF) 방식의 기업가치 평가
    """
    
    def __init__(self, initial_ebitda: float, terminal_growth_rate: float = 0.025,
                 wacc: float = 0.08):
        """
        Parameters
        ----------
        initial_ebitda : float
            초기 EBITDA
        terminal_growth_rate : float
            터미널 성장률
        wacc : float
            가중평균자본비용 (WACC)
        """
        self.initial_ebitda = initial_ebitda
        self.terminal_growth_rate = terminal_growth_rate
        self.wacc = wacc
    
    def project_cash_flows(self, years: int, growth_rate: float) -> np.ndarray:
        """
        현금흐름 예측
        
        Parameters
        ----------
        years : int
            예측 기간 (년)
        growth_rate : float
            연간 성장률
        
        Returns
        -------
        np.ndarray
            예측 EBITDA
        """
        ebitdas = []
        for i in range(years):
            ebitda = self.initial_ebitda * ((1 + growth_rate) ** (i + 1))
            ebitdas.append(ebitda)
        
        return np.array(ebitdas)
    
    def calculate_fcf(self, ebitda: np.ndarray, tax_rate: float = 0.25,
                     capex_pct: float = 0.05, nwc_change: float = 0) -> np.ndarray:
        """
        자유현금흐름(FCF) 계산
        
        FCF = EBITDA × (1 - 세율) - CapEx - NWC 변화
        """
        ebit = ebitda  # 간단히, D&A = 0으로 가정
        nopat = ebit * (1 - tax_rate)
        capex = ebitda * capex_pct
        fcf = nopat - capex - nwc_change
        
        return fcf
    
    def calculate_terminal_value(self, final_ebitda: float, 
                                exit_multiple: float = 7.0) -> float:
        """
        터미널 가치 계산
        
        Parameters
        ----------
        final_ebitda : float
            마지막 해 EBITDA
        exit_multiple : float
            출구 배수 (EV/EBITDA)
        
        Returns
        -------
        float
            터미널 가치
        """
        terminal_value = final_ebitda * exit_multiple
        return terminal_value
    
    def calculate_enterprise_value(self, fcf: np.ndarray, terminal_value: float) -> float:
        """
        기업가치(Enterprise Value) 계산
        """
        pv_fcf = sum(fcf[i] / (1 + self.wacc) ** (i + 1) for i in range(len(fcf)))
        pv_terminal = terminal_value / (1 + self.wacc) ** len(fcf)
        
        enterprise_value = pv_fcf + pv_terminal
        
        return enterprise_value


class LBOModel:
    """
    LBO (Leveraged Buyout) 모델
    
    부채를 활용하여 기업을 인수하는 거래 구조를 분석합니다.
    """
    
    def __init__(self, purchase_price: float, equity_contribution: float,
                 debt_amount: float, interest_rate: float = 0.06,
                 loan_term: int = 5):
        """
        Parameters
        ----------
        purchase_price : float
            인수 가격
        equity_contribution : float
            자본 투자액
        debt_amount : float
            차입액
        interest_rate : float
            이자율
        loan_term : int
            대출 기간 (년)
        """
        self.purchase_price = purchase_price
        self.equity_contribution = equity_contribution
        self.debt_amount = debt_amount
        self.interest_rate = interest_rate
        self.loan_term = loan_term
        
        # 검증
        if abs((equity_contribution + debt_amount) - purchase_price) > 1:
            raise ValueError("자본 + 부채 = 인수 가격이어야 합니다.")
    
    def get_capital_structure(self) -> Dict:
        """자본 구조 분석"""
        total_financing = self.equity_contribution + self.debt_amount
        
        return {
            'equity': self.equity_contribution,
            'debt': self.debt_amount,
            'total': total_financing,
            'equity_ratio': self.equity_contribution / total_financing,
            'debt_ratio': self.debt_amount / total_financing,
            'debt_to_equity': self.debt_amount / self.equity_contribution if self.equity_contribution > 0 else 0
        }
    
    def calculate_debt_schedule(self, annual_repayment: float) -> pd.DataFrame:
        """
        부채 상환 일정 계산
        
        Parameters
        ----------
        annual_repayment : float
            연간 상환액
        
        Returns
        -------
        pd.DataFrame
            부채 상환 일정
        """
        schedule = []
        remaining_debt = self.debt_amount
        
        for year in range(self.loan_term):
            interest_expense = remaining_debt * self.interest_rate
            principal_repayment = min(annual_repayment - interest_expense, remaining_debt)
            
            if principal_repayment < 0:
                print("경고: 상환액이 이자보다 작습니다.")
                principal_repayment = 0
            
            remaining_debt -= principal_repayment
            
            schedule.append({
                'year': year + 1,
                'beginning_debt': remaining_debt + principal_repayment,
                'interest_expense': interest_expense,
                'principal_repayment': principal_repayment,
                'ending_debt': remaining_debt
            })
        
        return pd.DataFrame(schedule)
    
    def calculate_exit_proceeds(self, exit_enterprise_value: float, 
                               remaining_debt: float, transaction_costs: float = 0) -> Dict:
        """
        출구 시 현금 회수 계산
        
        Parameters
        ----------
        exit_enterprise_value : float
            출구 시 기업가치
        remaining_debt : float
            남은 부채
        transaction_costs : float
            거래 비용
        
        Returns
        -------
        dict
            자본금과 부채에 대한 회수액
        """
        equity_proceeds = exit_enterprise_value - remaining_debt - transaction_costs
        
        return {
            'exit_enterprise_value': exit_enterprise_value,
            'debt_repayment': remaining_debt,
            'transaction_costs': transaction_costs,
            'equity_proceeds': equity_proceeds
        }


class PrivateEquityMetrics:
    """
    사모펀드 성과 지표
    
    - IRR (Internal Rate of Return)
    - MOIC (Multiple on Invested Capital)
    - DPI, RVPI, TVPI
    """
    
    @staticmethod
    def calculate_irr(cash_flows: Dict[int, float]) -> float:
        """
        IRR (내부수익률) 계산
        
        Parameters
        ----------
        cash_flows : dict
            {year: cash_flow}
        
        Returns
        -------
        float
            IRR
        """
        from numpy_financial import irr
        
        # 연도별로 정렬하여 현금흐름 배열 생성
        years = sorted(cash_flows.keys())
        max_year = max(years)
        
        # 0에서 max_year까지의 모든 연도에 대해 배열 생성
        cf_array = [0] * (max_year + 1)
        for year, cf in cash_flows.items():
            cf_array[year] = cf
        
        # IRR 계산
        return float(irr(cf_array))
    
    @staticmethod
    def calculate_moic(invested_capital: float, proceeds: float) -> float:
        """
        MOIC (Multiple on Invested Capital) 계산
        
        투자금 대비 회수금의 배수
        """
        return proceeds / invested_capital if invested_capital > 0 else 0
    
    @staticmethod
    def calculate_fund_metrics(called_capital: float, distributed_capital: float,
                              residual_value: float) -> Dict:
        """
        펀드 지표 계산
        
        Parameters
        ----------
        called_capital : float
            출자된 자본금
        distributed_capital : float
            배분된 자본금 (현금 회수)
        residual_value : float
            남은 포지션의 가치
        
        Returns
        -------
        dict
            DPI, RVPI, TVPI
        """
        # DPI: Distributed to Paid-in Capital Ratio
        dpi = distributed_capital / called_capital if called_capital > 0 else 0
        
        # RVPI: Residual Value to Paid-in Capital Ratio
        rvpi = residual_value / called_capital if called_capital > 0 else 0
        
        # TVPI: Total Value to Paid-in Capital Ratio
        tvpi = dpi + rvpi
        
        return {
            'dpi': dpi,
            'rvpi': rvpi,
            'tvpi': tvpi
        }


class LBOAnalysisSummary:
    """
    LBO 분석 요약
    """
    
    @staticmethod
    def generate_summary(lbo_model: LBOModel, dcf_model: DCFValuation,
                        entry_multiple: float, exit_multiple: float,
                        revenue_growth: float = 0.1) -> Dict:
        """
        LBO 거래 전체 분석 요약
        """
        # 자본 구조
        structure = lbo_model.get_capital_structure()
        
        # 현금흐름 예측 (5년)
        ebitdas = dcf_model.project_cash_flows(5, revenue_growth)
        fcf = dcf_model.calculate_fcf(ebitdas)
        
        # 터미널 값
        final_ebitda = ebitdas[-1]
        terminal_value = dcf_model.calculate_terminal_value(final_ebitda, exit_multiple)
        
        # 기업 가치
        enterprise_value = dcf_model.calculate_enterprise_value(fcf, terminal_value)
        
        # 출구 수익
        remaining_debt = lbo_model.debt_amount * 0.6  # 대략 60% 남아있다고 가정
        exit_proceeds = lbo_model.calculate_exit_proceeds(enterprise_value, remaining_debt)
        
        # 수익률
        moic = PrivateEquityMetrics.calculate_moic(
            lbo_model.equity_contribution,
            exit_proceeds['equity_proceeds']
        )
        
        return {
            'capital_structure': structure,
            'entry_multiple': entry_multiple,
            'exit_multiple': exit_multiple,
            'initial_enterprise_value': lbo_model.purchase_price,
            'exit_enterprise_value': enterprise_value,
            'moic': moic,
            'equity_invested': lbo_model.equity_contribution,
            'equity_proceeds': exit_proceeds['equity_proceeds'],
            'total_cash_generated': exit_proceeds['equity_proceeds'],
            'leverage_multiple': structure['debt_to_equity']
        }


# 사용 예제
if __name__ == "__main__":
    print("="*70)
    print("사모펀드 (Private Equity) 투자 분석")
    print("="*70)
    
    # LBO 거래 예제
    print("\n1. LBO 거래 구조")
    print("-"*70)
    
    purchase_price = 1000000000  # $1B
    equity = 300000000           # $300M (30%)
    debt = 700000000             # $700M (70%)
    
    lbo = LBOModel(purchase_price, equity, debt, interest_rate=0.06, loan_term=5)
    
    structure = lbo.get_capital_structure()
    print(f"\n구매 가격: ${purchase_price:,.0f}")
    print(f"자본 (Equity): ${structure['equity']:,.0f} ({structure['equity_ratio']*100:.1f}%)")
    print(f"부채 (Debt): ${structure['debt']:,.0f} ({structure['debt_ratio']*100:.1f}%)")
    print(f"부채/자본 비율: {structure['debt_to_equity']:.2f}x")
    
    # DCF 분석
    print("\n\n2. 기업 가치 평가 (DCF)")
    print("-"*70)
    
    initial_ebitda = 150000000  # $150M
    dcf = DCFValuation(initial_ebitda, terminal_growth_rate=0.025, wacc=0.08)
    
    ebitdas = dcf.project_cash_flows(5, growth_rate=0.10)
    print(f"\n예상 EBITDA (연간 10% 성장):")
    for year, ebitda in enumerate(ebitdas):
        print(f"  Year {year+1}: ${ebitda:,.0f}")
    
    # 출구 분석
    print("\n\n3. 출구 수익 분석")
    print("-"*70)
    
    exit_value = 1500000000  # $1.5B
    remaining_debt = debt * 0.5  # 절반 상환
    
    exit_proceeds = lbo.calculate_exit_proceeds(exit_value, remaining_debt)
    print(f"\n출구 시 기업가치: ${exit_proceeds['exit_enterprise_value']:,.0f}")
    print(f"남은 부채 상환: ${exit_proceeds['debt_repayment']:,.0f}")
    print(f"자본 수익: ${exit_proceeds['equity_proceeds']:,.0f}")
    
    # 수익률 계산
    moic = PrivateEquityMetrics.calculate_moic(equity, exit_proceeds['equity_proceeds'])
    print(f"\nMOIC: {moic:.2f}x")
    
    multiple = exit_proceeds['equity_proceeds'] / equity
    print(f"자본 배수: {multiple:.2f}x")
