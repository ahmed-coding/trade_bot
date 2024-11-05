class FibonacciStrategy:
    def __init__(self, data, trade_type="short_term"):
        """
        تهيئة البيانات اللازمة للاستراتيجية وتحديد نوع التداول (قصير أو طويل المدى)
        """
        self.data = data
        self.trade_type = trade_type
        self.levels = self.calculate_levels()

    def calculate_levels(self):
        high = max(self.data)
        low = min(self.data)
        
        levels = {
            "level_0": high,
            "level_23.6": high - 0.236 * (high - low),
            "level_38.2": high - 0.382 * (high - low),
            "level_50": high - 0.5 * (high - low),
            "level_61.8": high - 0.618 * (high - low),
            "level_100": low
        }
        return levels

    def should_enter_trade(self):
        """
        تحديد ما إذا كان يجب الدخول في الصفقة بناءً على نوع التداول وحالة السوق
        """
        if self.trade_type == "short_term":
            return self.data[-1] < self.levels["level_38.2"]
        else:
            return self.data[-1] < self.levels["level_61.8"]

    def update_strategy(self, new_data):
        """
        تحديث مستويات الاستراتيجية باستخدام بيانات جديدة لتحسين الأداء
        """
        self.data.extend(new_data)
        self.levels = self.calculate_levels()
