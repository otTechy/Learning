import pandas as pd
from xbbg import blp
from datetime import datetime

# Define ETF tickers and weights
etf_weights = {
    'SPY': 0.20, 'VXUS': 0.15, 'QQQ': 0.10,
    'SCHD': 0.10, 'VIG': 0.05, 'AGG': 0.10,
    'TIP': 0.05, 'HYG': 0.05, 'VNQ': 0.05,
    'GLD': 0.03, 'BOTZ': 0.07, 'SMH': 0.05
}

tickers = list(etf_weights.keys())
bbg_tickers = [f"{tkr} US Equity" for tkr in tickers]
# Add benchmark indices
benchmarks = {'SPMARC5P Index': 'SPMARC5P Index', 'SPXFRRE7 Index': 'SPXFRRE7 Index'}
bench_tickers = list(benchmarks.values())

start_date = "2019-01-01"
end_date = datetime.today().strftime('%Y-%m-%d')

# Download ETF and benchmark data from Bloomberg
all_tickers = bbg_tickers + bench_tickers
data = blp.bdh(all_tickers, flds=['PX_LAST'], start_date=start_date, end_date=end_date, Per='M')
adj_close = data.xs('PX_LAST', axis=1, level=1)
adj_close.columns = tickers + list(benchmarks.keys())
adj_close.dropna(inplace=True)

# Monthly returns and portfolio performance
monthly_returns = adj_close[tickers].pct_change().dropna()
weights_series = pd.Series(etf_weights)
portfolio_returns = monthly_returns.dot(weights_series)
cumulative_returns = (1 + portfolio_returns).cumprod()

# Benchmark returns
bench_returns = adj_close[list(benchmarks.keys())].pct_change().dropna()
bench_cum_returns = (1 + bench_returns).cumprod()

# Output results
performance_df = pd.DataFrame({
    "Portfolio Monthly Return": portfolio_returns,
    "Portfolio Cumulative Return": cumulative_returns,
    "SPMARC5P Monthly Return": bench_returns['SPMARC5P Index'],
    "SPMARC5P Cumulative Return": bench_cum_returns['SPMARC5P Index'],
    "SPXFRRE7 Monthly Return": bench_returns['SPXFRRE7 Index'],
    "SPXFRRE7 Cumulative Return": bench_cum_returns['SPXFRRE7 Index']
})
print(performance_df)
