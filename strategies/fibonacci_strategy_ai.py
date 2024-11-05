import os
import pickle
from sklearn.linear_model import LinearRegression
import numpy as np

class FibonacciStrategyAI:
    def __init__(self, data, trade_type="short_term"):
        self.data = data
        self.trade_type = trade_type
        self.model = None
        self.model_path = os.path.join("models", "fibonacci_model.pkl")
        self.levels = self.calculate_levels()
        
        # تحميل النموذج إذا كان موجودًا، أو تدريب نموذج جديد
        if os.path.exists(self.model_path):
            with open(self.model_path, "rb") as file:
                self.model = pickle.load(file)
        else:
            self.train_model()  # تدريب نموذج جديد إذا لم يكن موجودًا

    def calculate_levels(self):
        high = max(self.data)
        low = min(self.data)
        
        levels = {
            "level_0": high,
            "level_23.6": high - 0.236 * (high - low),
            "level_38.2": high - 0.382 * (high - low),
            "level_50": high - 0.5 * (high - low),
            "level_61.8": high - 0.618 * (high - low),
            "level_100": low
        }
        return levels

    def train_model(self):
        """
        تدريب نموذج الانحدار الخطي باستخدام بيانات السعر التاريخية وحفظه في ملف
        """
        prices = np.array(range(len(self.data))).reshape(-1, 1)
        values = np.array(self.data).reshape(-1, 1)
        
        self.model = LinearRegression()
        self.model.fit(prices, values)
        
        # حفظ النموذج في ملف
        with open(self.model_path, "wb") as file:
            pickle.dump(self.model, file)
        print("تم تدريب وحفظ نموذج Fibonacci بنجاح")

    def predict_next_price(self):
        """
        التنبؤ بالسعر المستقبلي باستخدام النموذج المدرب
        """
        next_time_step = np.array([[len(self.data)]])
        predicted_price = self.model.predict(next_time_step)
        return predicted_price[0][0]

    def should_enter_trade(self):
        predicted_price = self.predict_next_price()
        if self.trade_type == "short_term":
            return predicted_price < self.levels["level_38.2"]
        else:
            return predicted_price < self.levels["level_61.8"]

    def update_strategy(self, new_data):
        """
        تحديث مستويات الاستراتيجية وتدريب النموذج على البيانات الجديدة وحفظه
        """
        self.data.extend(new_data)
        self.levels = self.calculate_levels()
        self.train_model()  # إعادة تدريب النموذج بالبيانات الجديدة
