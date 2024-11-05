import os
import pickle
from sklearn.linear_model import LinearRegression
import numpy as np

class FairValueGapStrategyAI:
    def __init__(self, data, trade_type="short_term"):
        self.data = data
        self.trade_type = trade_type
        self.model = None
        self.model_path = os.path.join("models", "fair_value_gap_model.pkl")

        if os.path.exists(self.model_path):
            with open(self.model_path, "rb") as file:
                self.model = pickle.load(file)
        else:
            self.train_model()

    def train_model(self):
        prices = np.array(range(len(self.data))).reshape(-1, 1)
        values = np.array(self.data).reshape(-1, 1)
        
        self.model = LinearRegression()
        self.model.fit(prices, values)
        
        with open(self.model_path, "wb") as file:
            pickle.dump(self.model, file)
        print("تم تدريب وحفظ نموذج Fair Value Gap بنجاح")

    def predict_gap(self):
        next_step = np.array([[len(self.data)]])
        predicted_price = self.model.predict(next_step)
        return predicted_price[0][0]

    def should_enter_trade(self):
        predicted_price = self.predict_gap()
        avg_price = sum(self.data[-5:]) / 5
        if self.trade_type == "short_term":
            return predicted_price < avg_price * 0.98
        else:
            return predicted_price < avg_price * 0.95

    def update_strategy(self, new_data):
        self.data.extend(new_data)
        self.train_model()
