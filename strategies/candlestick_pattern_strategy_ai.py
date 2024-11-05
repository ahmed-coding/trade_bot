import os
import pickle
from sklearn.neural_network import MLPClassifier
import numpy as np

class CandlestickPatternStrategyAI:
    def __init__(self, data, trade_type="short_term"):
        self.data = data
        self.trade_type = trade_type
        self.model = None
        self.model_path = os.path.join("models", "candlestick_model.pkl")

        if os.path.exists(self.model_path):
            with open(self.model_path, "rb") as file:
                self.model = pickle.load(file)
        else:
            self.train_model()

    def extract_features(self, candles):
        open_prices = [c["open"] for c in candles]
        close_prices = [c["close"] for c in candles]
        return [max(open_prices), min(open_prices), sum(close_prices) / len(close_prices)]

    def train_model(self):
        features = np.array([self.extract_features(self.data[i:i+5]) for i in range(len(self.data)-5)])
        labels = np.array([1 if self.data[i+5]["close"] > self.data[i+4]["close"] else 0 for i in range(len(self.data)-5)])
        
        self.model = MLPClassifier(hidden_layer_sizes=(50,), max_iter=500)
        self.model.fit(features, labels)
        
        with open(self.model_path, "wb") as file:
            pickle.dump(self.model, file)
        print("تم تدريب وحفظ نموذج Candlestick بنجاح")

    def predict_pattern(self):
        features = np.array(self.extract_features(self.data[-5:])).reshape(1, -1)
        return self.model.predict(features)[0] == 1

    def should_enter_trade(self):
        return self.predict_pattern()

    def update_strategy(self, new_data):
        self.data.extend(new_data)
        self.train_model()
