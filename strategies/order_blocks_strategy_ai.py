import os
import pickle
from sklearn.ensemble import AdaBoostClassifier
import numpy as np

class OrderBlocksStrategyAI:
    timeframe = 'long'
    def __init__(self, data, trade_type="long"):
        self.data = data
        self.trade_type = trade_type
        self.model = None
        self.model_path = os.path.join("models", "order_blocks_model.pkl")

        if os.path.exists(self.model_path):
            with open(self.model_path, "rb") as file:
                self.model = pickle.load(file)
        else:
            self.train_model()

    def detect_order_block(self):
        avg_price = sum(self.data[-5:]) / 5
        return avg_price

    def train_model(self):
        features = np.array([self.data[i-5:i] for i in range(5, len(self.data))])
        labels = np.array([1 if max(features[i]) > sum(features[i])/len(features[i]) else 0 for i in range(len(features))])

        self.model = AdaBoostClassifier()
        self.model.fit(features, labels)

        with open(self.model_path, "wb") as file:
            pickle.dump(self.model, file)
        print("تم تدريب وحفظ نموذج Order Blocks بنجاح")

    def should_enter_trade(self):
        avg_price = self.detect_order_block()
        return self.data[-1] > avg_price if self.trade_type == "short" else self.data[-1] < avg_price

    def update_strategy(self, new_data):
        self.data.extend(new_data)
        self.train_model()
