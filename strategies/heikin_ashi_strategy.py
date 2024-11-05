class HeikinAshiStrategy:
    def __init__(self, data, trade_type="short_term"):
        self.data = data
        self.trade_type = trade_type

    def calculate_heikin_ashi(self):
        """
        حساب الشموع بطريقة هيكين آشي
        """
        ha_close = sum([candle["close"] for candle in self.data[-4:]]) / 4
        ha_open = (self.data[-2]["open"] + self.data[-2]["close"]) / 2
        return ha_open < ha_close if self.trade_type == "short_term" else ha_open > ha_close

    def should_enter_trade(self):
        return self.calculate_heikin_ashi()

    def update_strategy(self, new_data):
        self.data.extend(new_data)
