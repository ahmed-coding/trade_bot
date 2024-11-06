import os
import pickle
from sklearn.ensemble import RandomForestClassifier
import numpy as np

class OscillatorsStrategyAI:
    def __init__(self, data, trade_type="short"):
        self.data = data
        self.trade_type = trade_type
        self.model = None
        self.model_path = os.path.join("models", "oscillators_model.pkl")

        if os.path.exists(self.model_path):
            with open(self.model_path, "rb") as file:
                self.model = pickle.load(file)
        else:
            self.train_model()

    def calculate_oscillator(self):
        average = sum(self.data[-10:]) / 10
        return self.data[-1] - average

    def train_model(self):
        features = np.array([self.data[i] - sum(self.data[i-10:i])/10 for i in range(10, len(self.data))]).reshape(-1, 1)
        labels = np.array([1 if self.data[i] > self.data[i-1] else 0 for i in range(10, len(self.data))])

        self.model = RandomForestClassifier()
        self.model.fit(features, labels)

        with open(self.model_path, "wb") as file:
            pickle.dump(self.model, file)
        print("تم تدريب وحفظ نموذج Oscillators بنجاح")

    def should_enter_trade(self):
        oscillator = self.calculate_oscillator()
        return oscillator > 0 if self.trade_type == "short_term" else oscillator < 0

    def update_strategy(self, new_data):
        self.data.extend(new_data)
        self.train_model()
