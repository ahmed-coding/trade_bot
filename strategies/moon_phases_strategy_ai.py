import os
import pickle
from sklearn.linear_model import LogisticRegression
import numpy as np
import ephem
from datetime import datetime

class MoonPhasesStrategyAI:
    def __init__(self, data, trade_type="long"):
        self.data = data
        self.moon_phase = self.get_moon_phase()  # احصل على مرحلة القمر الحالية بدقة عالية
        self.trade_type = trade_type
        self.model = None
        self.model_path = os.path.join("models", "moon_phases_model.pkl")

        if os.path.exists(self.model_path):
            with open(self.model_path, "rb") as file:
                self.model = pickle.load(file)
        else:
            self.train_model()

    def get_moon_phase(self):
        """احسب مرحلة القمر الحالية بدقة باستخدام مكتبة ephem."""
        moon = ephem.Moon()
        moon.compute(datetime.utcnow())
        phase = moon.phase

        # إرجاع المرحلة الدقيقة بناءً على قيمة إضاءة القمر
        if phase == 0:
            return "new_moon"
        elif 0 < phase < 25:
            return "waxing_crescent"
        elif phase == 25:
            return "first_quarter"
        elif 25 < phase < 50:
            return "waxing_gibbous"
        elif phase == 50:
            return "full_moon"
        elif 50 < phase < 75:
            return "waning_gibbous"
        elif phase == 75:
            return "last_quarter"
        else:
            return "waning_crescent"

    def train_model(self):
        # تحويل مرحلة القمر إلى بيانات قابلة للاستخدام
        phases = [self.get_phase_value(phase) for phase in [self.moon_phase] * (len(self.data) - 3)]
        features = np.array([self.data[i:i+3] + [phases[i]] for i in range(len(self.data)-3)])
        labels = np.array([1 if self.data[i+3] > self.data[i+2] else 0 for i in range(len(self.data)-3)])
        
        self.model = LogisticRegression()
        self.model.fit(features, labels)
        
        with open(self.model_path, "wb") as file:
            pickle.dump(self.model, file)
        print("تم تدريب وحفظ نموذج Moon Phases بنجاح")

    def get_phase_value(self, phase_name):
        """تحويل اسم المرحلة إلى قيمة رقمية لاستخدامها في التدريب"""
        phase_mapping = {
            "new_moon": 0,
            "waxing_crescent": 1,
            "first_quarter": 2,
            "waxing_gibbous": 3,
            "full_moon": 4,
            "waning_gibbous": 5,
            "last_quarter": 6,
            "waning_crescent": 7
        }
        return phase_mapping.get(phase_name, 0)

    def predict_phase_impact(self):
        # استخدام المرحلة الحالية للقمر للتنبؤ
        phase_indicator = self.get_phase_value(self.moon_phase)
        features = np.array(self.data[-3:] + [phase_indicator]).reshape(1, -1)
        return self.model.predict(features)[0] == 1

    def should_enter_trade(self):
        return self.predict_phase_impact()

    def update_strategy(self, new_data):
        self.data.extend(new_data)
        self.moon_phase = self.get_moon_phase()  # تحديث مرحلة القمر
        self.train_model()
