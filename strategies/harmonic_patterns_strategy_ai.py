import os
import pickle
from sklearn.neighbors import KNeighborsClassifier
import numpy as np

class HarmonicPatternsStrategyAI:
    def __init__(self, data, trade_type="short_term"):
        self.data = data
        self.trade_type = trade_type
        self.model = None
        self.model_path = os.path.join("models", "harmonic_patterns_model.pkl")

        if os.path.exists(self.model_path):
            with open(self.model_path, "rb") as file:
                self.model = pickle.load(file)
        else:
            self.train_model()

    def train_model(self):
        features = np.array([self.data[i:i+5] for i in range(len(self.data)-5)])
        labels = np.array([1 if max(self.data[i:i+5]) - min(self.data[i:i+5]) > 0 else 0 for i in range(len(self.data)-5)])
        
        self.model = KNeighborsClassifier(n_neighbors=3)
        self.model.fit(features, labels)
        
        with open(self.model_path, "wb") as file:
            pickle.dump(self.model, file)
        print("تم تدريب وحفظ نموذج Harmonic Patterns بنجاح")

    def predict_pattern(self):
        features = np.array(self.data[-5:]).reshape(1, -1)
        return self.model.predict(features)[0] == 1

    def should_enter_trade(self):
        return self.predict_pattern()

    def update_strategy(self, new_data):
        self.data.extend(new_data)
        self.train_model()
