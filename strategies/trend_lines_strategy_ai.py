import os
import pickle
from sklearn.linear_model import LinearRegression
import numpy as np

class TrendLinesStrategyAI:
    timeframe = 'long'
    def __init__(self, data, trade_type="long"):
        self.data = data
        self.trade_type = trade_type
        self.model = None
        self.model_path = os.path.join("models", "trend_lines_model.pkl")

        if os.path.exists(self.model_path):
            with open(self.model_path, "rb") as file:
                self.model = pickle.load(file)
        else:
            self.train_model()

    def calculate_trend_line(self):
        x = np.arange(len(self.data)).reshape(-1, 1)
        y = np.array(self.data).reshape(-1, 1)
        self.model = LinearRegression().fit(x, y)
        trend_slope = self.model.coef_[0][0]
        return trend_slope

    def train_model(self):
        self.calculate_trend_line()
        
        with open(self.model_path, "wb") as file:
            pickle.dump(self.model, file)
        print("تم تدريب وحفظ نموذج Trend Lines بنجاح")

    def should_enter_trade(self):
        trend_slope = self.calculate_trend_line()
        return trend_slope > 0 if self.trade_type == "short_term" else trend_slope < 0

    def update_strategy(self, new_data):
        self.data.extend(new_data)
        self.train_model()
