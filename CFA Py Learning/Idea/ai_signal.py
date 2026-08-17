import pandas as pd
import numpy as np
from xbbg import blp
from datetime import datetime
import argparse
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Simple AI signal detection for ETF/stock tickers

def parse_list(str_value):
    return [item.strip() for item in str_value.split(',') if item.strip()]

def fetch_data(tickers, start_date, end_date):
    bbg_tickers = [f"{tkr} US Equity" for tkr in tickers]
    data = blp.bdh(bbg_tickers, flds=['PX_LAST'], start_date=start_date, end_date=end_date, Per='D')
    adj_close = data.xs('PX_LAST', axis=1, level=1)
    adj_close.columns = tickers
    adj_close.dropna(inplace=True)
    return adj_close

def engineer_features(df):
    # Example: use returns, moving averages, volatility as features
    features = pd.DataFrame(index=df.index)
    for tkr in df.columns:
        features[f'{tkr}_ret1'] = df[tkr].pct_change()
        features[f'{tkr}_ma5'] = df[tkr].rolling(5).mean()
        features[f'{tkr}_ma20'] = df[tkr].rolling(20).mean()
        features[f'{tkr}_vol'] = df[tkr].rolling(10).std()
    features = features.dropna()
    return features

def create_labels(df, threshold=0.01):
    # Example: label 1 if next day return > threshold, else 0
    labels = (df.pct_change().shift(-1) > threshold).astype(int)
    labels = labels.dropna()
    return labels

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tickers', type=str, required=True, help='Comma-separated tickers (e.g. SPY,QQQ)')
    parser.add_argument('--start_date', type=str, required=True)
    parser.add_argument('--end_date', type=str, required=True)
    args = parser.parse_args()
    tickers = parse_list(args.tickers)
    start_date = args.start_date
    end_date = args.end_date

    df = fetch_data(tickers, start_date, end_date)
    features = engineer_features(df)
    labels = create_labels(df)
    # Align features and labels
    features, labels = features.align(labels, join='inner', axis=0)
    for tkr in tickers:
        X = features[[col for col in features.columns if col.startswith(tkr)]]
        y = labels[tkr]
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
        clf = RandomForestClassifier(n_estimators=100, random_state=42)
        clf.fit(X_train, y_train)
        y_pred = clf.predict(X_test)
        print(f"\nSignal report for {tkr}:")
        print(classification_report(y_test, y_pred))

if __name__ == "__main__":
    main()
