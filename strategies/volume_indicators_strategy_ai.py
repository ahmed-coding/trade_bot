import os
import pickle
from sklearn.svm import SVR
import numpy as np

class VolumeIndicatorsStrategyAI:
    def __init__(self, data, volumes, trade_type="short_term"):
        self.data = data
        self.volumes = volumes
        self.trade_type = trade_type
        self.model = None
        self.model_path = os.path.join("models", "volume_indicators_model.pkl")

        if os.path.exists(self.model_path):
            with open(self.model_path, "rb") as file:
                self.model = pickle.load(file)
        else:
            self.train_model()

    def calculate_volume_trend(self):
        return np.corrcoef(self.data[-10:], self.volumes[-10:])[0, 1]

    def train_model(self):
        features = np.array(self.volumes[-10:]).reshape(-1, 1)
        labels = np.array([1 if self.data[i] > self.data[i-1] else 0 for i in range(1, len(self.data))])
        
        self.model = SVR()
        self.model.fit(features, labels)
        
        with open(self.model_path, "wb") as file:
            pickle.dump(self.model, file)
        print("تم تدريب وحفظ نموذج Volume Indicators بنجاح")

    def should_enter_trade(self):
        volume_trend = self.calculate_volume_trend()
        return volume_trend > 0.5 if self.trade_type == "short_term" else volume_trend < 0.5

    def update_strategy(self, new_data, new_volumes):
        self.data.extend(new_data)
        self.volumes.extend(new_volumes)
        self.train_model()
