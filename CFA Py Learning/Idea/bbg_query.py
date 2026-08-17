import blpapi
from xbbg import blp

def get_bbg_data(ticker: str, fields: list, start_date: str = None, end_date: str = None):
    """
    Query Bloomberg for data using xbbg. Requires Bloomberg Terminal and license.
    :param ticker: Bloomberg ticker, e.g. 'AAPL US Equity'
    :param fields: List of Bloomberg fields, e.g. ['PX_LAST', 'VOLATILITY_30D']
    :param start_date: Optional start date (YYYY-MM-DD)
    :param end_date: Optional end date (YYYY-MM-DD)
    :return: DataFrame with results
    """
    if start_date and end_date:
        df = blp.bdh(ticker, fields, start_date, end_date)
    else:
        df = blp.bdp(ticker, fields)
    return df

if __name__ == "__main__":
    # Example usage
    ticker = input("Enter Bloomberg ticker (e.g. 'AAPL US Equity'): ")
    fields = input("Enter fields separated by comma (e.g. 'PX_LAST,VOLATILITY_30D'): ").split(',')
    start_date = input("Start date (YYYY-MM-DD, optional): ") or None
    end_date = input("End date (YYYY-MM-DD, optional): ") or None
    data = get_bbg_data(ticker, fields, start_date, end_date)
    print(data)
