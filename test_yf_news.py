import yfinance as yf

def test_news(ticker_symbol):
    print(f"Testing news for {ticker_symbol}...")
    ticker = yf.Ticker(ticker_symbol)
    news = ticker.news
    if news:
        print(f"Found {len(news)} news items.")
        for item in news[:3]:
            print(f"- {item.get('title')} ({item.get('publisher')})")
    else:
        print("No news items found.")

if __name__ == "__main__":
    test_news("EURUSD=X")
    test_news("USDINR=X")
