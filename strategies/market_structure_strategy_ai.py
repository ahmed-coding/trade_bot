import os
import pickle
from sklearn.tree import DecisionTreeClassifier
import numpy as np

class MarketStructureStrategyAI:
    timeframe = 'short'
    def __init__(self, data, trade_type="short"):
        self.data = data
        self.trade_type = trade_type
        self.model = None
        self.model_path = os.path.join("models", "market_structure_model.pkl")

        if os.path.exists(self.model_path):
            with open(self.model_path, "rb") as file:
                self.model = pickle.load(file)
        else:
            self.train_model()

    def calculate_structure(self):
        high = max(self.data[-10:])
        low = min(self.data[-10:])
        return high, low

    def train_model(self):
        features = np.array([self.data[i-10:i] for i in range(10, len(self.data))])
        labels = np.array([1 if max(features[i]) - min(features[i]) > 0 else 0 for i in range(len(features))])

        self.model = DecisionTreeClassifier()
        self.model.fit(features, labels)

        with open(self.model_path, "wb") as file:
            pickle.dump(self.model, file)
        print("تم تدريب وحفظ نموذج Market Structure بنجاح")

    def should_enter_trade(self):
        high, low = self.calculate_structure()
        return self.data[-1] > high if self.trade_type == "short_term" else self.data[-1] < low

    def update_strategy(self, new_data):
        self.data.extend(new_data)
        self.train_model()
