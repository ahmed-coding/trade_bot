import os
import pickle
from sklearn.svm import SVC
import numpy as np

class DivergenceStrategyAI:
    def __init__(self, data, volumes, trade_type="short_term"):
        self.data = [float(value) for value in data]
        self.volumes = [float(volume) for volume in volumes]
        self.trade_type = trade_type
        self.model = None
        self.model_path = os.path.join("models", "divergence_model.pkl")

        if os.path.exists(self.model_path):
            with open(self.model_path, "rb") as file:
                self.model = pickle.load(file)
        else:
            self.train_model()

    def calculate_divergence(self):
        price_change = self.data[-1] - self.data[-2]
        volume_change = self.volumes[-1] - self.volumes[-2]
        return price_change * volume_change

    def train_model(self):
        features = np.array([[self.data[i] - self.data[i-1], self.volumes[i] - self.volumes[i-1]] for i in range(1, len(self.data))])
        labels = np.array([1 if features[i][0] * features[i][1] > 0 else 0 for i in range(len(features))])

        if len(set(labels)) < 2:
            print("تنبيه: البيانات تحتوي على فئة واحدة فقط في labels، غير كافية للتدريب.")
            return

        self.model = SVC()
        self.model.fit(features, labels)

        with open(self.model_path, "wb") as file:
            pickle.dump(self.model, file)
        print("تم تدريب وحفظ نموذج Divergence بنجاح")

    def should_enter_trade(self):
        divergence = self.calculate_divergence()
        return divergence > 0 if self.trade_type == "short_term" else divergence < 0

    def update_strategy(self, new_data, new_volumes):
        self.data.extend([float(value) for value in new_data])
        self.volumes.extend([float(volume) for volume in new_volumes])
        self.train_model()
