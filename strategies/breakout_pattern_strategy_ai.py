import os
import pickle
from sklearn.tree import DecisionTreeClassifier
import numpy as np

class BreakoutPatternStrategyAI:
    def __init__(self, data, trade_type="short_term"):
        self.data = data
        self.trade_type = trade_type
        self.model = None
        self.model_path = os.path.join("models", "breakout_model.pkl")
        
        # تحميل النموذج إذا كان موجودًا، أو تدريب نموذج جديد
        if os.path.exists(self.model_path):
            with open(self.model_path, "rb") as file:
                self.model = pickle.load(file)
        else:
            self.train_model()  # تدريب نموذج جديد إذا لم يكن موجودًا

    def train_model(self):
        """
        تدريب نموذج شجرة القرار باستخدام بيانات الأنماط السابقة وحفظه
        """
        features = np.array([self.data[i:i+10] for i in range(len(self.data)-10)]).reshape(-1, 10)
        labels = np.array([1 if self.data[i+10] > max(self.data[i:i+10]) else 0 for i in range(len(self.data)-10)])
        
        self.model = DecisionTreeClassifier()
        self.model.fit(features, labels)
        
        # حفظ النموذج في ملف
        with open(self.model_path, "wb") as file:
            pickle.dump(self.model, file)
        print("تم تدريب وحفظ نموذج Breakout بنجاح")

    def predict_breakout(self):
        features = np.array(self.data[-10:]).reshape(1, -1)
        return self.model.predict(features)[0] == 1

    def should_enter_trade(self):
        return self.predict_breakout()

    def update_strategy(self, new_data):
        self.data.extend(new_data)
        self.train_model()
