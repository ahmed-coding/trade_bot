class ElliotWaveStrategy:
    def __init__(self, data, trade_type="short_term"):
        self.data = data
        self.trade_type = trade_type

    def detect_elliot_wave(self):
        """
        تحليل موجات إليوت لتحديد إشارات الدخول
        """
        if len(self.data) >= 5:
            if self.data[-1] > self.data[-3] and self.data[-2] < self.data[-4]:
                return True if self.trade_type == "long_term" else False
        return False

    def should_enter_trade(self):
        """
        تحديد ما إذا كان يجب دخول الصفقة بناءً على تحليل موجات إليوت
        """
        return self.detect_elliot_wave()

    def update_strategy(self, new_data):
        """
        تحسين الاستراتيجية باستخدام البيانات الجديدة
        """
        self.data.extend(new_data)
