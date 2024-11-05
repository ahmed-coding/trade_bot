class BreakoutPatternStrategy:
    def __init__(self, data, trade_type="short_term"):
        """
        تهيئة البيانات اللازمة للاستراتيجية وتحديد نوع التداول (قصير أو طويل المدى)
        """
        self.data = data
        self.trade_type = trade_type

    def identify_breakout(self):
        recent_high = max(self.data[-10:])
        recent_low = min(self.data[-10:])
        
        if self.trade_type == "short_term":
            if self.data[-1] > recent_high:
                return "breakout_up"
            elif self.data[-1] < recent_low:
                return "breakout_down"
        else:
            long_term_high = max(self.data)
            long_term_low = min(self.data)
            if self.data[-1] > long_term_high:
                return "breakout_up"
            elif self.data[-1] < long_term_low:
                return "breakout_down"
        return None

    def should_enter_trade(self):
        """
        تحديد ما إذا كان يجب الدخول في الصفقة بناءً على نمط الانفصال
        """
        breakout = self.identify_breakout()
        return breakout == "breakout_up"

    def update_strategy(self, new_data):
        """
        تحديث استراتيجية نمط الانفصال بناءً على البيانات الجديدة لتحسين الأداء
        """
        self.data.extend(new_data)
