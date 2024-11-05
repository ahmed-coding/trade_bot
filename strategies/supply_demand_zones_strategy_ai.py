import os
import pickle
from sklearn.ensemble import RandomForestClassifier
import numpy as np

class SupplyDemandZonesStrategyAI:
    def __init__(self, data, trade_type="short_term"):
        self.data = data
        self.trade_type = trade_type
        self.model = None
        self.model_path = os.path.join("models", "supply_demand_zones_model.pkl")

        if os.path.exists(self.model_path):
            with open(self.model_path, "rb") as file:
                self.model = pickle.load(file)
        else:
            self.train_model()

    def calculate_supply_demand_zones(self):
        high = max(self.data[-10:])
        low = min(self.data[-10:])
        return high, low

    def train_model(self):
        features = np.array([self.data[i-10:i] for i in range(10, len(self.data))])
        labels = np.array([1 if max(features[i]) - min(features[i]) > 0 else 0 for i in range(len(features))])

        self.model = RandomForestClassifier()
        self.model.fit(features, labels)

        with open(self.model_path, "wb") as file:
            pickle.dump(self.model, file)
        print("تم تدريب وحفظ نموذج Supply and Demand Zones بنجاح")

    def should_enter_trade(self):
        high, low = self.calculate_supply_demand_zones()
        return self.data[-1] < low if self.trade_type == "short_term" else self.data[-1] > high

    def update_strategy(self, new_data):
        self.data.extend(new_data)
        self.train_model()