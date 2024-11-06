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

    def train_model(self):
        # التأكد من طول البيانات وتفادي أي أخطاء في الأبعاد
        min_length = min(len(self.data), len(self.volumes)) - 1
        features = np.array([[self.data[i], self.volumes[i]] for i in range(min_length)])
        labels = np.array([1 if self.data[i + 1] > self.data[i] else 0 for i in range(min_length)])

        # التأكد من توافق طول features و labels
        if len(features) == len(labels) and len(features) > 0:
            self.model = SVR()
            self.model.fit(features, labels)
            with open(self.model_path, "wb") as file:
                pickle.dump(self.model, file)
            print("تم تدريب وحفظ نموذج Volume Indicators بنجاح")
        else:
            print("تنبيه: البيانات تحتوي على عدد غير متساوٍ من features و labels. التدريب غير ممكن.")

    def should_enter_trade(self):
        if len(self.data) > 0 and len(self.volumes) > 0:
            recent_data = np.array([[self.data[-1], self.volumes[-1]]]).reshape(1, -1)
            prediction = self.model.predict(recent_data)[0]
            return prediction > 0
        return False

    def update_strategy(self, new_data, new_volumes):
        self.data.extend(new_data)
        self.volumes.extend(new_volumes)
        self.train_model()
