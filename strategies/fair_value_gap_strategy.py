class FairValueGapStrategy:
    def __init__(self, data, trade_type="short_term"):
        self.data = data
        self.trade_type = trade_type

    def identify_gap(self):
        """
        اكتشاف فجوة القيمة العادلة كإشارة تداول
        """
        avg_price = sum(self.data[-5:]) / len(self.data[-5:])
        if self.trade_type == "short_term":
            return self.data[-1] < avg_price * 0.98
        else:
            return self.data[-1] < avg_price * 0.95

    def should_enter_trade(self):
        """
        تحديد ما إذا كان يجب دخول الصفقة بناءً على فجوة القيمة العادلة
        """
        return self.identify_gap()

    def update_strategy(self, new_data):
        self.data.extend(new_data)
