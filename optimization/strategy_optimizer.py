# optimization/strategy_optimizer.py
from strategy_loader import load_strategies  # استيراد الدالة التي قمنا بإنشائها لتحميل الاستراتيجيات
import numpy as np

class StrategyOptimizer:
    def __init__(self, data, target_variable, max_iterations=100):
        self.data = data
        self.target_variable = target_variable
        self.max_iterations = max_iterations
        self.strategies = load_strategies()  # تحميل الاستراتيجيات بشكل ديناميكي

    def optimize_strategies(self):
        """تحسين جميع الاستراتيجيات المتاحة باستخدام البيانات."""
        results = {}
        for strategy_name, strategy_class in self.strategies.items():
            print(f"تحسين الاستراتيجية: {strategy_name}")
            strategy_instance = strategy_class(self.data)

            # إجراء التحسين (مثلاً، ضبط المعلمات وتدريب النموذج)
            performance = self.optimize_strategy(strategy_instance)
            results[strategy_name] = performance
            print(f"أداء الاستراتيجية {strategy_name}: {performance}")
        
        return results

    def optimize_strategy(self, strategy_instance):
        """تنفيذ خطوات التحسين لاستراتيجية معينة."""
        best_score = -np.inf
        for _ in range(self.max_iterations):
            score = strategy_instance.train_and_evaluate(self.target_variable)
            if score > best_score:
                best_score = score
        return best_score
