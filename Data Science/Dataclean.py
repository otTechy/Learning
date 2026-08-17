import pandas as pd
import numpy as np

"""
Step 1 – Load Data
==================
Load raw FX trade data into a pandas DataFrame.

In production, this data is sourced from Snowflake:
    Table : SPYDER_DEV_DB.RECLUSE_REPORTS.TBL_FX_REPORT
    Filter: OBSERVATIONDATE >= '2026-04-01'

For this demo, a representative sample is constructed inline to simulate
the structure and common data-quality issues found in real FX report data.

What this shows you: Real financial data is messy. Note the deliberate problems I planted:

COUNTERPARTYID has a None
NOTIONAL mixes integers and a string with comma ('25,000,000'), plus one trade with a notional of 100 (almost certainly in millions — unit confusion!)
CURRENCY_PAIR has inconsistent casing ('eur/usd' vs 'EUR/USD')
TRADE_DATE is in three different formats

"""

df = pd.DataFrame({
    'INTERNALID':     ['T001', 'T002', 'T003', 'T004', 'T005'],
    'COUNTERPARTY':   ['JPM', 'JPM', 'DB', 'DB', 'C'],
    'COUNTERPARTYID': ['JP-9912', 'JP-9913', None, 'DB-441', 'C-7723'],
    'NOTIONAL':       [50_000_000, '25,000,000', 100, 75_000_000, 30_000_000],
    'CURRENCY_PAIR':  ['EUR/USD', 'eur/usd', 'GBP/USD', 'USD/JPY', 'EUR/USD'],
    'TRADE_DATE':     ['2026-04-15', '2026-04-15', '2026/04/16', '2026-04-17', '04-18-2026'],
    'MATURITY_DATE':  ['2026-05-15', '2026-07-15', '2026-05-16', '2026-04-19', '2026-05-18'],
    'RATE':           [1.0850, 1.0852, 1.2734, 152.30, 1.0845],
    'OBSERVATIONDATE':['2026-04-20', '2026-04-20', '2026-04-20', '2026-04-20', '2026-04-20'],
})
print(df)

# step 2: check data
# The first command of any data engineering session — always
"""Watch for: Anytime a column you expect to be numeric shows as object, something is wrong. Investigate before doing anything else."""
print(df.info())
print("\nMissing values per column:")
print(df.isna().sum())
print("\nNumeric column stats:")
print(df.describe())

# step 3: clean up data
# Notional: clean the comma-separated strings then convert to float
df['NOTIONAL'] = (
    df['NOTIONAL']
    .astype(str)                    # ensure everything is a string first
    .str.replace(',', '')           # remove commas
    .str.replace('$', '')           # remove dollar signs if any
    .astype(float)                  # convert to float
)

# Dates: pandas can usually figure out mixed formats with `format='mixed'`
df['TRADE_DATE'] = pd.to_datetime(df['TRADE_DATE'], format='mixed', errors='coerce')
df['MATURITY_DATE'] = pd.to_datetime(df['MATURITY_DATE'], format='mixed', errors='coerce')
df['OBSERVATIONDATE'] = pd.to_datetime(df['OBSERVATIONDATE'], errors='coerce')

# Strings: normalize case and strip whitespace
df['CURRENCY_PAIR'] = df['CURRENCY_PAIR'].str.upper().str.strip()
df['COUNTERPARTY'] = df['COUNTERPARTY'].str.upper().str.strip()

print(df.dtypes)
print(df.head())

# step 4: Sanity check on notional magnitudes
# In production, you don't silently fix these. You log them, flag them for review, and have a deliberate decision rule. Maybe drop them, maybe multiply by 1M based on the CP's known convention, maybe escalate to ops. 
expected_min_fx_notional = 100_000   # FX trades below 100k are unusual at institutional scale

suspicious = df[df['NOTIONAL'] < expected_min_fx_notional]
print(f"Trades with suspiciously small notional: {len(suspicious)}")
print(suspicious[['INTERNALID', 'COUNTERPARTY', 'NOTIONAL']])


# step 5: handle missing value
# Missing CP ID — this is the variable you're trying to predict matches for!
# How you handle missing values DEPENDS on what they mean.

# Option A: drop the row (when missingness means "unusable")
df_clean = df.dropna(subset=['COUNTERPARTYID'])

# Option B: keep with a sentinel (when missingness is informative)
df['HAS_CP_ID'] = df['COUNTERPARTYID'].notna()
df['COUNTERPARTYID'] = df['COUNTERPARTYID'].fillna('MISSING') # fill na with "missing" string to keep the record but mark it as missing

print(f"Original rows: {len(df)}, after handling missing CP ID: {len(df_clean)}")

# step 6: handle edge case and cp specific rules
# Always log what you did and how many records were affected
# Tenor in days — how long the trade lasts
df['TENOR_DAYS'] = (df['MATURITY_DATE'] - df['TRADE_DATE']).dt.days

# Notional in millions for readability
df['NOTIONAL_MM'] = df['NOTIONAL'] / 1_000_000

# Days since trade (relative to observation date)
df['DAYS_SINCE_TRADE'] = (df['OBSERVATIONDATE'] - df['TRADE_DATE']).dt.days

# Currency pair: split into base/quote currencies
df[['BASE_CCY', 'QUOTE_CCY']] = df['CURRENCY_PAIR'].str.split('/', expand=True)

print(df[['INTERNALID', 'TENOR_DAYS', 'NOTIONAL_MM', 'BASE_CCY', 'QUOTE_CCY']])

#step 7: final check to validate clean data
def validate_clean_data(df):
    """A checklist function — run on every cleaned dataset."""
    issues = []
    
    # Check 1: any unexpected types
    expected_types = {
        'NOTIONAL': 'float64',
        'TRADE_DATE': 'datetime64[ns]',
        'MATURITY_DATE': 'datetime64[ns]',
    }
    for col, expected in expected_types.items():
        actual = str(df[col].dtype)
        if actual != expected:
            issues.append(f"❌ {col} is {actual}, expected {expected}")
    
    # Check 2: tenor sanity (no negative tenors!)
    if (df['TENOR_DAYS'] < 0).any():
        issues.append(f"❌ {(df['TENOR_DAYS'] < 0).sum()} trades have negative tenor")
    
    # Check 3: observation date >= trade date (no future trades)
    if (df['OBSERVATIONDATE'] < df['TRADE_DATE']).any():
        issues.append(f"❌ Some trades have OBSERVATIONDATE before TRADE_DATE — time travel!")
    
    # Check 4: no NaN in critical columns
    critical = ['INTERNALID', 'NOTIONAL', 'TRADE_DATE']
    for col in critical:
        if df[col].isna().any():
            issues.append(f"❌ NaN in critical column {col}")
    
    if issues:
        print("VALIDATION FAILED:")
        for i in issues: print(f"  {i}")
    else:
        print("✅ All validation checks passed")
    return len(issues) == 0

validate_clean_data(df)


# Overall script
import pandas as pd
import numpy as np
from snowflake.connector import connect
from datetime import datetime

def load_fx_trades(start_date: str, end_date: str) -> pd.DataFrame:
    """Load FX trades from Snowflake with validation."""
    
    # In production, use environment variables or secrets manager
    conn = connect(
        user='YOUR_USER',
        password='YOUR_PASSWORD',   # NEVER hardcode — use env vars
        account='eldridge-derivatives',
        warehouse='YOUR_WH',
        database='SPYDER_DEV_DB',
        schema='RECLUSE_REPORTS',
    )
    
    query = """
    SELECT 
        INTERNALID,
        COUNTERPARTY,
        COUNTERPARTYID,
        NOTIONAL,
        CURRENCY_PAIR,
        TRADE_DATE,
        MATURITY_DATE,
        RATE,
        OBSERVATIONDATE
    FROM TBL_FX_REPORT
    WHERE OBSERVATIONDATE BETWEEN %s AND %s
    """
    df = pd.read_sql(query, conn, params=(start_date, end_date))
    conn.close()
    return df


def clean_fx_trades(df: pd.DataFrame) -> pd.DataFrame:
    """Apply all cleaning steps. Return a cleaned, validated DataFrame."""
    
    df = df.copy()  # never mutate the input
    
    # Type coercion
    df['NOTIONAL'] = pd.to_numeric(df['NOTIONAL'], errors='coerce')
    for date_col in ['TRADE_DATE', 'MATURITY_DATE', 'OBSERVATIONDATE']:
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
    
    # String normalization
    df['CURRENCY_PAIR'] = df['CURRENCY_PAIR'].str.upper().str.strip()
    df['COUNTERPARTY'] = df['COUNTERPARTY'].str.upper().str.strip()
    
    # Flag missing CP ID rather than drop — it's predictive
    df['HAS_CP_ID'] = df['COUNTERPARTYID'].notna()
    
    # Sanity check notionals
    suspicious_count = (df['NOTIONAL'] < 100_000).sum()
    if suspicious_count > 0:
        print(f"⚠️  {suspicious_count} trades with notional < $100k — flagged for review")
        df['NOTIONAL_FLAG'] = df['NOTIONAL'] < 100_000
    
    # Derived fields
    df['TENOR_DAYS'] = (df['MATURITY_DATE'] - df['TRADE_DATE']).dt.days
    df['NOTIONAL_MM'] = df['NOTIONAL'] / 1_000_000
    df['DAYS_SINCE_TRADE'] = (df['OBSERVATIONDATE'] - df['TRADE_DATE']).dt.days
    df[['BASE_CCY', 'QUOTE_CCY']] = df['CURRENCY_PAIR'].str.split('/', expand=True)
    
    # Drop rows with critical NaN (notional, dates, internal ID)
    before = len(df)
    df = df.dropna(subset=['INTERNALID', 'NOTIONAL', 'TRADE_DATE', 'MATURITY_DATE'])
    print(f"Dropped {before - len(df)} rows with missing critical fields")
    
    return df


def validate_fx_trades(df: pd.DataFrame) -> bool:
    """Run validation suite. Return True if all checks pass."""
    issues = []
    
    if (df['TENOR_DAYS'] < 0).any():
        issues.append(f"{(df['TENOR_DAYS'] < 0).sum()} trades with negative tenor")
    
    if (df['OBSERVATIONDATE'] < df['TRADE_DATE']).any():
        issues.append("Observation date before trade date (time travel)")
    
    if df['NOTIONAL'].isna().any():
        issues.append(f"{df['NOTIONAL'].isna().sum()} trades with NaN notional after cleaning")
    
    if issues:
        print("❌ VALIDATION FAILED:")
        for i in issues: print(f"   {i}")
        return False
    print(f"✅ All checks passed on {len(df)} trades")
    return True


# Full pipeline
df_raw = load_fx_trades('2026-04-01', '2026-04-30')
df_clean = clean_fx_trades(df_raw)
assert validate_fx_trades(df_clean), "Data validation failed"

# Save the cleaned dataset for downstream sessions
df_clean.to_parquet('fx_trades_clean_apr2026.parquet')
print(f"Saved {len(df_clean)} clean records — ready for modeling")