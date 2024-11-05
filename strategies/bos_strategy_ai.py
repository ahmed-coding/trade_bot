import os
import pickle
from sklearn.ensemble import GradientBoostingClassifier
import numpy as np

class BOStrategyAI:
    def __init__(self, data, trade_type="short_term"):
        self.data = data
        self.trade_type = trade_type
        self.model = None
        self.model_path = os.path.join("models", "bos_model.pkl")

        if os.path.exists(self.model_path):
            with open(self.model_path, "rb") as file:
                self.model = pickle.load(file)
        else:
            self.train_model()

    def detect_break_of_structure(self):
        recent_high = max(self.data[-10:])
        recent_low = min(self.data[-10:])
        return self.data[-1] > recent_high or self.data[-1] < recent_low

    def train_model(self):
        features = np.array([self.data[i-10:i] for i in range(10, len(self.data))])
        labels = np.array([1 if features[i][-1] > max(features[i]) or features[i][-1] < min(features[i]) else 0 for i in range(len(features))])

        self.model = GradientBoostingClassifier()
        self.model.fit(features, labels)

        with open(self.model_path, "wb") as file:
            pickle.dump(self.model, file)
        print("تم تدريب وحفظ نموذج Break of Structure بنجاح")

    def should_enter_trade(self):
        return self.detect_break_of_structure()

    def update_strategy(self, new_data):
        self.data.extend(new_data)
        self.train_model()
