class MoonPhasesStrategy:
    def __init__(self, data, moon_phase, trade_type="short_term"):
        self.data = data
        self.moon_phase = moon_phase  # 'full' or 'new'
        self.trade_type = trade_type

    def should_enter_trade(self):
        """
        تحليل مراحل القمر كإشارة تداول
        """
        if self.moon_phase == "full":
            return True if self.trade_type == "short_term" else False
        return False

    def update_strategy(self, new_data, new_moon_phase):
        self.data.extend(new_data)
        self.moon_phase = new_moon_phase
