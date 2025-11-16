# 📊 파생상품 및 헤지펀드 시뮬레이션 대시보드 (확장판)

## 프로젝트 개요

이 대시보드는 교재 **Chapter 13 (Derivatives)** 및 **Chapter 9 (Hedge Funds and Private Equity)** 의 내용을 통합하여,
금융 파생상품과 대체투자 전략을 시뮬레이션하고 분석하는 교육용 도구입니다.

## 📚 포함된 내용

### Chapter 13: 파생상품 (Derivatives)

#### 옵션 가격 결정 모델
- **Black-Scholes 모델**: 유럽형 옵션의 이론적 가격 계산
- **Greeks 분석**: Delta, Gamma, Theta, Vega, Rho
- **손익 시뮬레이션**: 다양한 옵션 전략의 손익 곡선
- **내재 변동성**: 시장 옵션 가격에서 변동성 역산

#### 선물
- **이론적 선물 가격**: \(F = S \times e^{(r-q)T}\)
- **베이시스 분석**: 정상시장(Contango) vs 역조시장(Backwardation)
- **차익거래 분석**: 가격 오류 감지

#### 기타 파생상품
- 스왑: 금리 스왑, 통화 스왑
- 복합 전략: 스트래들, 스트랭글, 스프레드

### Chapter 9: 헤지펀드 및 사모펀드

#### 헤지펀드 전략
- **롱/숏 전략**: 저평가 자산 매수 + 고평가 자산 공매도
- **페어 트레이딩**: 상관관계 높은 자산쌍 거래
- **시장 중립**: 시장 방향과 무관한 절대수익 추구

#### 레버리지 분석
- **레버리지 효과**: 자본 배수에 따른 손익 변화
- **마진 콜**: 위험 선점 및 리스크 관리
- **차입 비용**: 레버리지 이용의 실질 비용

#### 사모펀드 (Private Equity)
- **LBO 모델**: 부채를 활용한 인수 거래 구조
- **DCF 평가**: 현금흐름 할인 방식의 기업가치 평가
- **수익률 분석**: IRR, MOIC, DPI/RVPI/TVPI

#### 포트폴리오 리스크 관리
- **VaR**: Value at Risk 계산
- **CVaR**: Conditional VaR (Expected Shortfall)
- **포트폴리오 최적화**: 샤프 비율 최대화
- **상관관계 분석**: 다각화 효과

## 🏗️ 프로젝트 구조

```
derivatives-dashboard/
├── app.py                          # 메인 Streamlit 애플리케이션
├── requirements.txt                # 필수 패키지
├── README.md                       # 프로젝트 개요
│
├── models/                         # 금융 모델
│   ├── black_scholes.py           # Black-Scholes 옵션 모델
│   ├── futures.py                 # 선물 모델
│   ├── hedge_fund_strategies.py   # 헤지펀드 전략 (NEW)
│   ├── risk_management.py         # 리스크 관리 (NEW)
│   └── private_equity.py          # 사모펀드 모델 (NEW)
│
├── utils/                         # 유틸리티
│   ├── visualization.py           # Plotly 차트 생성
│   └── calculations.py            # 금융 계산 함수
│
├── pages/                         # Streamlit 멀티페이지
│   ├── 1_📈_Options_Calculator.py
│   ├── 2_📊_Futures_Calculator.py
│   ├── 3_🎯_Greeks_Analysis.py
│   ├── 6_🎯_Hedge_Fund_Strategies.py   # (NEW)
│   ├── 7_🛡️_Risk_Management.py         # (NEW)
│   └── 8_💼_Private_Equity.py          # (NEW)
│
├── data/                          # 샘플 데이터
├── tests/                         # 단위 테스트
├── docs/                          # 문서
└── .github/workflows/             # CI/CD

```

## 🎯 핵심 기능

### 1️⃣ 옵션 계산기
```python
from models.black_scholes import BlackScholesModel

bs = BlackScholesModel(S=100, K=105, T=30/365, r=0.05, sigma=0.20)
call_price = bs.call_price()
greeks = bs.get_all_greeks('call')
```

**입력**: 기초자산 가격, 행사가격, 만기, 이자율, 변동성  
**출력**: 옵션 가격, Greeks, 손익 곡선

### 2️⃣ 롱/숏 전략 시뮬레이터
```python
from models.hedge_fund_strategies import LongShortStrategy

ls = LongShortStrategy(initial_capital=1000000, leverage_ratio=2.0)
ls.add_long_position('AAPL', 150.0, 1000)
ls.add_short_position('MSFT', 300.0, 500)
result = ls.calculate_positions_value(long_prices, short_prices)
```

**특징**: 시장 중립 전략, 레버리지, 절대수익률 추구

### 3️⃣ 레버리지 분석
```python
from models.hedge_fund_strategies import Leverage

scenarios = Leverage.leverage_scenarios(
    initial_investment=1000000,
    price_change_pct=0.05,
    leverage_ratios=[1.0, 2.0, 3.0, 5.0]
)

margin_call = Leverage.margin_call_price(entry_price=100, leverage_ratio=3.0)
```

**마진 콜 경고**: 레버리지 3배일 때 약 33% 하락 시 마진 콜 발생

### 4️⃣ VaR 계산
```python
from models.risk_management import VaRCalculator

var_calc = VaRCalculator(returns, confidence_level=0.95)
historical_var = var_calc.historical_var(portfolio_value=1000000)
cvar = var_calc.conditional_var(portfolio_value=1000000)
```

### 5️⃣ LBO 모델링
```python
from models.private_equity import LBOModel, DCFValuation

lbo = LBOModel(
    purchase_price=1000000000,
    equity_contribution=300000000,
    debt_amount=700000000
)

dcf = DCFValuation(initial_ebitda=150000000)
enterprise_value = dcf.calculate_enterprise_value(fcf, terminal_value)
```

## 🚀 설치 및 실행

### 1. 환경 구성

```bash
# 폴더 이동
cd derivatives-dashboard

# 가상환경 생성
python -m venv venv

# 가상환경 활성화 (Windows)
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# 패키지 설치
pip install -r requirements.txt
```

### 2. 애플리케이션 실행

```bash
streamlit run app.py
```

브라우저에서 자동으로 `http://localhost:8501` 접속

## 📖 사용 가이드

### 옵션 분석
1. "📈 옵션 계산기" 선택
2. 파라미터 입력 (기초자산, 행사가, 만기 등)
3. "💰 계산하기" 버튼 클릭
4. Greeks 및 손익 곡선 확인

### 헤지펀드 전략
1. "🎯 헤지펀드 전략" 선택
2. 롱/숏 포지션 입력
3. 레버리지 배율 선택
4. 포트폴리오 성과 및 시장 노출도 분석

### 리스크 관리
1. "🛡️ 리스크 관리" 선택
2. 포트폴리오 구성 입력
3. VaR 및 최대 드로우다운 계산
4. 포트폴리오 최적화 결과 확인

### 사모펀드 분석
1. "💼 사모펀드" 선택
2. LBO 거래 구조 입력
3. DCF 기업가치 평가 수행
4. 출구 수익률(IRR, MOIC) 분석

## 📊 주요 개념

### Greeks (옵션 민감도)

| Greek | 정의 | 범위 | 활용 |
|-------|------|------|------|
| **Delta (Δ)** | 기초자산 $1 변화 시 옵션 가격 변화 | Call: 0~1<br>Put: -1~0 | 헷지 비율 |
| **Gamma (Γ)** | Delta의 변화율 | 항상 양수 | 포지션 동적 조정 |
| **Theta (Θ)** | 시간 경과에 따른 가격 감소 | 일반적 음수 | 시간 가치 측정 |
| **Vega (ν)** | 변동성 1% 변화 시 가격 변화 | 항상 양수 | 변동성 트레이딩 |
| **Rho (ρ)** | 이자율 1% 변화 시 가격 변화 | Call: 양수<br>Put: 음수 | 금리 민감도 |

### 헤지펀드 전략 특성

| 전략 | 목표 | 장점 | 위험 |
|------|------|------|------|
| **롱/숏** | 절대수익률 | 시장 무관, 분산 | 복잡성, 비용 |
| **시장중립** | 최소화 | 저 변동성 | 높은 기술력 필요 |
| **페어 트레이딩** | 스프레드 수익 | 저 상관관계 | 상관도 변화 |

### 리스크 지표

- **VaR (Value at Risk)**: 신뢰수준 95%에서 일일 최대 손실액
- **CVaR**: VaR을 초과하는 손실의 평균
- **샤프 비율**: (수익률 - 무위험율) / 변동성
- **최대 드로우다운**: 최고점에서 최저점까지 하락률

## 💡 실전 예제

### 예제 1: 옵션 헷징
```
포지션: 주식 1,000주 @ $100
위험: 주가 하락
해결: Put 옵션으로 보호

계산:
- Put 옵션 (K=$95): 비용 $2
- 하락 시: 최대 손실 5% (행사가) + 2% (프리미엄) = 7%
```

### 예제 2: 절대수익 추구
```
롱 포지션: Apple 1,000주 @ $150
숏 포지션: Microsoft 500주 @ $300
레버리지: 2배

기대: 시장 상승/하락과 무관하게 상대적 가치 차이로 수익
```

### 예제 3: LBO 거래
```
인수 대상: $1B 기업 (EBITDA $150M)
자본 구조: 70% 부채 ($700M), 30% 자본 ($300M)
기대 수익: 5년 후 매각, 3배 자본 회수 (IRR 25%+)
```

## 📚 참고 자료

### 이론 배경
- [Black-Scholes Model](https://en.wikipedia.org/wiki/Black%E2%80%93Scholes_model)
- [Options Greeks](https://www.investopedia.com/trading/using-the-greeks-to-understand-options/)
- [Hedge Funds](https://en.wikipedia.org/wiki/Hedge_fund)
- [Private Equity](https://en.wikipedia.org/wiki/Private_equity)

### 교재
- "An Introduction to Global Financial Markets" - Chapter 9, 13
- "Options, Futures, and Other Derivatives" - John Hull
- "The Handbook of Alternative Investments" - Mark J. P. Anson

### 라이브러리
- [NumPy](https://numpy.org/): 수치 계산
- [SciPy](https://scipy.org/): 통계 함수
- [Streamlit](https://streamlit.io/): 웹 프레임워크
- [Plotly](https://plotly.com/): 인터랙티브 시각화

## ⚠️ 면책 조항

이 대시보드는 **교육 목적**으로만 사용됩니다.

- 실제 투자 결정에 사용하지 마세요
- 계산 결과는 단순화되어 있습니다
- 실무에서는 전문가와 상담하세요
- 과거 성과는 미래를 보장하지 않습니다

## 🤝 기여하기

개선 사항이 있으면 GitHub Issues를 통해 제안해주세요.

## 📧 문의

질문이나 버그 리포트는 GitHub 이슈를 생성해주세요.

---

**Made for Financial Education** 🎓
