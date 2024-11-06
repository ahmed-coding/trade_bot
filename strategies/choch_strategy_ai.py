import os
import pickle
from sklearn.neural_network import MLPClassifier
import numpy as np

class ChochStrategyAI:
    def __init__(self, data, trade_type="short"):
        self.data = data
        self.trade_type = trade_type
        self.model = None
        self.model_path = os.path.join("models", "choch_model.pkl")

        if os.path.exists(self.model_path):
            with open(self.model_path, "rb") as file:
                self.model = pickle.load(file)
        else:
            self.train_model()

    def detect_change_of_character(self):
        avg_price = sum(self.data[-10:]) / 10
        return self.data[-1] > avg_price if self.trade_type == "short_term" else self.data[-1] < avg_price

    def train_model(self):
        features = np.array([self.data[i-10:i] for i in range(10, len(self.data))])
        labels = np.array([1 if features[i][-1] > sum(features[i]) / len(features[i]) else 0 for i in range(len(features))])

        self.model = MLPClassifier(hidden_layer_sizes=(50,), max_iter=500)
        self.model.fit(features, labels)

        with open(self.model_path, "wb") as file:
            pickle.dump(self.model, file)
        print("تم تدريب وحفظ نموذج CHoCH بنجاح")

    def should_enter_trade(self):
        return self.detect_change_of_character()

    def update_strategy(self, new_data):
        self.data.extend(new_data)
        self.train_model()
