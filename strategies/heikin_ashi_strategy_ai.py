import os
import pickle
from sklearn.svm import SVC
import numpy as np

class HeikinAshiStrategyAI:
    def __init__(self, data, trade_type="short_term"):
        self.data = data
        self.trade_type = trade_type
        self.model = None
        self.model_path = os.path.join("models", "heikin_ashi_model.pkl")

        if os.path.exists(self.model_path):
            with open(self.model_path, "rb") as file:
                self.model = pickle.load(file)
        else:
            self.train_model()

    def train_model(self):
        features = np.array([self.data[i:i+4] for i in range(len(self.data)-4)])
        labels = np.array([1 if self.data[i+4] > self.data[i+3] else 0 for i in range(len(self.data)-4)])
        
        self.model = SVC()
        self.model.fit(features, labels)
        
        with open(self.model_path, "wb") as file:
            pickle.dump(self.model, file)
        print("تم تدريب وحفظ نموذج Heikin Ashi بنجاح")

    def predict_heikin_ashi(self):
        features = np.array(self.data[-4:]).reshape(1, -1)
        return self.model.predict(features)[0] == 1

    def should_enter_trade(self):
        return self.predict_heikin_ashi()

    def update_strategy(self, new_data):
        self.data.extend(new_data)
        self.train_model()

