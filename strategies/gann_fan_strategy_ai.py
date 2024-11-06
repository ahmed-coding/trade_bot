import os
import pickle
from sklearn.linear_model import LinearRegression
import numpy as np

class GannFanStrategyAI:
    timeframe = 'long'
    def __init__(self, data, trade_type="long"):
        self.data = data
        self.trade_type = trade_type
        self.model = None
        self.model_path = os.path.join("models", "gann_fan_model.pkl")

        if os.path.exists(self.model_path):
            with open(self.model_path, "rb") as file:
                self.model = pickle.load(file)
        else:
            self.train_model()

    def calculate_gann_angle(self):
        x = np.arange(len(self.data)).reshape(-1, 1)
        y = np.array(self.data).reshape(-1, 1)
        self.model = LinearRegression().fit(x, y)
        gann_angle = self.model.coef_[0][0]
        return gann_angle

    def train_model(self):
        self.calculate_gann_angle()
        
        with open(self.model_path, "wb") as file:
            pickle.dump(self.model, file)
        print("تم تدريب وحفظ نموذج Gann Fan بنجاح")

    def should_enter_trade(self):
        gann_angle = self.calculate_gann_angle()
        return gann_angle > 0 if self.trade_type == "short_term" else gann_angle < 0

    def update_strategy(self, new_data):
        self.data.extend(new_data)
        self.train_model()
