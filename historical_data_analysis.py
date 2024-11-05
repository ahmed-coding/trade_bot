import requests
import pandas as pd
from datetime import datetime, timedelta

class CurrencySelector:
    def __init__(self, interval="1d", min_history_days=90):
        self.interval = interval
        self.min_history_days = min_history_days
        self.available_symbols = self.fetch_available_symbols()
        self.selected_symbols = []

    def fetch_available_symbols(self):
        """جمع قائمة العملات المتاحة للتداول على Binance"""
        url = "https://api.binance.com/api/v3/exchangeInfo"
        response = requests.get(url)
        data = response.json()
        symbols = [item["symbol"] for item in data["symbols"] if item["quoteAsset"] == "USDT"]
        print(f"تم جمع {len(symbols)} عملة من Binance")
        return symbols

    def fetch_currency_data(self, symbol):
        """جمع البيانات التاريخية للعملة"""
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=self.min_history_days)
        start_time_str = int(start_time.timestamp() * 1000)
        
        url = "https://api.binance.com/api/v3/klines"
        params = {
            "symbol": symbol,
            "interval": self.interval,
            "startTime": start_time_str,
        }
        response = requests.get(url, params=params)
        data = response.json()
        
        if len(data) < self.min_history_days:
            print(f"البيانات غير كافية للعملة {symbol}، تحتوي على {len(data)} يوم فقط.")
            return None
        
        df = pd.DataFrame(data, columns=["timestamp", "open", "high", "low", "close", "volume", "close_time", "quote_asset_volume", "number_of_trades", "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"])
        df["close"] = df["close"].astype(float)
        return df

    def is_currency_suitable(self, df):
        """تحديد ما إذا كانت العملة مناسبة للتداول بناءً على التحليل"""
        trend = df["close"].pct_change().mean()
        volatility = df["close"].pct_change().std()
        return trend > 0 and volatility < 0.05

    def select_currencies(self, max_currencies=50):
        """اختيار عدد محدد من العملات للتداول"""
        for symbol in self.available_symbols:
            if len(self.selected_symbols) >= max_currencies:
                break
            df = self.fetch_currency_data(symbol)
            if df is not None and self.is_currency_suitable(df):
                self.selected_symbols.append(symbol)
                print(f"تم اختيار العملة {symbol} للتداول")
        print(f"تم اختيار {len(self.selected_symbols)} عملة للتداول.")

    def get_selected_symbols(self):
        """إرجاع قائمة العملات المختارة"""
        return self.selected_symbols
