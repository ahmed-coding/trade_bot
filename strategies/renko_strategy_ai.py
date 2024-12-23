import os
import pickle
from sklearn.linear_model import Ridge
import numpy as np

class RenkoStrategyAI:
    timeframe = 'long'
    def __init__(self, data, brick_size=10, trade_type="long"):
        self.data = data
        self.brick_size = brick_size
        self.trade_type = trade_type
        self.model = None
        self.model_path = os.path.join("models", "renko_model.pkl")

        if os.path.exists(self.model_path):
            with open(self.model_path, "rb") as file:
                self.model = pickle.load(file)
        else:
            self.train_model()

    def calculate_renko(self):
        renko_chart = [self.data[i] for i in range(0, len(self.data), self.brick_size)]
        return renko_chart

    def train_model(self):
        bricks = self.calculate_renko()
        features = np.array(range(len(bricks))).reshape(-1, 1)
        values = np.array(bricks).reshape(-1, 1)
        
        self.model = Ridge()
        self.model.fit(features, values)
        
        with open(self.model_path, "wb") as file:
            pickle.dump(self.model, file)
        print("تم تدريب وحفظ نموذج Renko بنجاح")

    def predict_next_brick(self):
        next_step = np.array([[len(self.calculate_renko())]])
        predicted_price = self.model.predict(next_step)
        return predicted_price[0][0]

    def should_enter_trade(self):
        predicted_price = self.predict_next_brick()
        last_brick = self.calculate_renko()[-1]
        if self.trade_type == "short":
            return predicted_price > last_brick
        else:
            return predicted_price < last_brick

    def update_strategy(self, new_data):
        self.data.extend(new_data)
        self.train_model()
