import os
import pickle
from sklearn.linear_model import LogisticRegression
import numpy as np

class MoonPhasesStrategyAI:
    def __init__(self, data, moon_phase, trade_type="short_term"):
        self.data = data
        self.moon_phase = moon_phase  # 'full' or 'new'
        self.trade_type = trade_type
        self.model = None
        self.model_path = os.path.join("models", "moon_phases_model.pkl")

        if os.path.exists(self.model_path):
            with open(self.model_path, "rb") as file:
                self.model = pickle.load(file)
        else:
            self.train_model()

    def train_model(self):
        phases = [1 if phase == 'full' else 0 for phase in self.moon_phase]
        features = np.array([self.data[i:i+3] + [phases[i]] for i in range(len(self.data)-3)])
        labels = np.array([1 if self.data[i+3] > self.data[i+2] else 0 for i in range(len(self.data)-3)])
        
        self.model = LogisticRegression()
        self.model.fit(features, labels)
        
        with open(self.model_path, "wb") as file:
            pickle.dump(self.model, file)
        print("تم تدريب وحفظ نموذج Moon Phases بنجاح")

    def predict_phase_impact(self):
        features = np.array(self.data[-3:] + [1 if self.moon_phase == 'full' else 0]).reshape(1, -1)
        return self.model.predict(features)[0] == 1

    def should_enter_trade(self):
        return self.predict_phase_impact()

    def update_strategy(self, new_data, new_moon_phase):
        self.data.extend(new_data)
        self.moon_phase = new_moon_phase
        self.train_model()
