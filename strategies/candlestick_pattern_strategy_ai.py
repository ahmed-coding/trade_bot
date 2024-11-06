import os
import pickle
from sklearn.neural_network import MLPClassifier
import numpy as np

class CandlestickPatternStrategyAI:
    timeframe = 'short'
    def __init__(self, data, trade_type="short"):
        # تحويل البيانات إلى قائمة من القيم العددية لضمان أن تكون أعدادًا صحيحة
        self.data = [float(value) for value in data]
        self.trade_type = trade_type
        self.model = None
        self.model_path = os.path.join("models", "candlestick_model.pkl")

        if os.path.exists(self.model_path):
            with open(self.model_path, "rb") as file:
                self.model = pickle.load(file)
        else:
            self.train_model()

    def extract_features(self, prices):
        # التعامل مع الأسعار فقط (قائمة من القيم)
        return [max(prices), min(prices), sum(prices) / len(prices)]

    def train_model(self):
        # بناء الخصائص كقوائم من القيم
        features = np.array([self.extract_features(self.data[i:i+5]) for i in range(len(self.data)-5)])
        labels = np.array([1 if self.data[i+5] > self.data[i+4] else 0 for i in range(len(self.data)-5)])
        
        # تدريب النموذج
        self.model = MLPClassifier(hidden_layer_sizes=(50,), max_iter=500)
        self.model.fit(features, labels)
        
        with open(self.model_path, "wb") as file:
            pickle.dump(self.model, file)
        print("تم تدريب وحفظ نموذج Candlestick بنجاح")

    def predict_pattern(self):
        # استخدام آخر 5 أسعار فقط
        features = np.array(self.extract_features(self.data[-5:])).reshape(1, -1)
        return self.model.predict(features)[0] == 1

    def should_enter_trade(self):
        return self.predict_pattern()

    def update_strategy(self, new_data):
        # تحويل البيانات الجديدة إلى قائمة من القيم العددية
        self.data.extend([float(value) for value in new_data])
        self.train_model()
