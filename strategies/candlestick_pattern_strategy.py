class CandlestickPatternStrategy:
    def __init__(self, data, trade_type="short_term"):
        self.data = data
        self.trade_type = trade_type

    def detect_candlestick_pattern(self):
        """
        اكتشاف نمط الشموع اليابانية كإشارة دخول
        """
        if len(self.data) < 2:
            return None
        if self.data[-1]["close"] > self.data[-1]["open"] and self.data[-2]["close"] < self.data[-2]["open"]:
            return "bullish_engulfing" if self.trade_type == "short_term" else "long_term_bullish"
        return None

    def should_enter_trade(self):
        """
        تحليل النمط الياباني واتخاذ قرار الدخول
        """
        pattern = self.detect_candlestick_pattern()
        return pattern in ["bullish_engulfing", "long_term_bullish"]

    def update_strategy(self, new_data):
        """
        تحديث استراتيجية الشموع اليابانية باستخدام البيانات الجديدة
        """
        self.data.extend(new_data)
