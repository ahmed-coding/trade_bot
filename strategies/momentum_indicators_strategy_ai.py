import os
import pickle
from sklearn.linear_model import LogisticRegression
import numpy as np

class MomentumIndicatorsStrategyAI:
    def __init__(self, data, trade_type="short_term"):
        self.data = data
        self.trade_type = trade_type
        self.model = None
        self.model_path = os.path.join("models", "momentum_indicators_model.pkl")

        if os.path.exists(self.model_path):
            with open(self.model_path, "rb") as file:
                self.model = pickle.load(file)
        else:
            self.train_model()

    def calculate_momentum(self):
        if len(self.data) < 2:
            return 0
        return self.data[-1] - self.data[-2]

    def train_model(self):
        features = np.array([[self.data[i] - self.data[i - 1]] for i in range(1, len(self.data))])
        labels = np.array([1 if self.data[i] > self.data[i - 1] else 0 for i in range(1, len(self.data))])
        
        self.model = LogisticRegression()
        self.model.fit(features, labels)
        
        with open(self.model_path, "wb") as file:
            pickle.dump(self.model, file)
        print("تم تدريب وحفظ نموذج Momentum Indicators بنجاح")

    def should_enter_trade(self):
        momentum = self.calculate_momentum()
        return momentum > 0 if self.trade_type == "short_term" else momentum < 0

    def update_strategy(self, new_data):
        self.data.extend(new_data)
        self.train_model()
