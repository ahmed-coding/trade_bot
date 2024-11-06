import os
import pickle
from sklearn.linear_model import LinearRegression
import numpy as np

class DynamicSupportResistanceStrategyAI:
    timeframe = 'long'

    def __init__(self, data, trade_type="long"):
        self.data = data
        self.trade_type = trade_type
        self.model = None
        self.model_path = os.path.join("models", "dynamic_support_resistance_model.pkl")

        if os.path.exists(self.model_path):
            with open(self.model_path, "rb") as file:
                self.model = pickle.load(file)
        else:
            self.train_model()

    def calculate_dynamic_level(self):
        avg_price = sum(self.data[-10:]) / len(self.data[-10:])
        return avg_price

    def train_model(self):
        prices = np.array(range(len(self.data))).reshape(-1, 1)
        values = np.array(self.data).reshape(-1, 1)
        
        self.model = LinearRegression()
        self.model.fit(prices, values)
        
        with open(self.model_path, "wb") as file:
            pickle.dump(self.model, file)
        print("تم تدريب وحفظ نموذج Dynamic Support and Resistance بنجاح")

    def should_enter_trade(self):
        dynamic_level = self.calculate_dynamic_level()
        if self.trade_type == "short_term":
            return self.data[-1] > dynamic_level
        else:
            return self.data[-1] < dynamic_level

    def update_strategy(self, new_data):
        self.data.extend(new_data)
        self.train_model()
