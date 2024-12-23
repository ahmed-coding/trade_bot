import os
import pickle
from sklearn.linear_model import LogisticRegression
import numpy as np

class SupportResistanceStrategyAI:
    timeframe = 'long'
    def __init__(self, data, support_level, resistance_level, trade_type="long"):
        self.data = data
        self.support_level = support_level
        self.resistance_level = resistance_level
        self.trade_type = trade_type
        self.model = None
        self.model_path = os.path.join("models", "support_resistance_model.pkl")

        if os.path.exists(self.model_path):
            with open(self.model_path, "rb") as file:
                self.model = pickle.load(file)
        else:
            self.train_model()

    def train_model(self):
        features = np.array([self.data[i:i+3] for i in range(len(self.data)-3)])
        labels = np.array([1 if self.data[i+3] > self.data[i+2] else 0 for i in range(len(self.data)-3)])
        
        self.model = LogisticRegression()
        self.model.fit(features, labels)
        
        with open(self.model_path, "wb") as file:
            pickle.dump(self.model, file)
        print("تم تدريب وحفظ نموذج Support and Resistance بنجاح")

    def should_enter_trade(self):
        if self.trade_type == "short":
            return self.data[-1] < self.support_level
        else:
            return self.data[-1] > self.resistance_level

    def update_strategy(self, new_data, new_support_level, new_resistance_level):
        self.data.extend(new_data)
        self.support_level = new_support_level
        self.resistance_level = new_resistance_level
        self.train_model()
