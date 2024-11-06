import os
import importlib

def load_strategies():
    """تحميل جميع الاستراتيجيات الموجودة في مجلد 'strategies' ديناميكيًا."""
    strategies = {}
    strategies_path = "strategies"
    
    def convert_to_camel_case(filename):
        """تحويل اسم الملف إلى CamelCase ليكون اسم الفئة المقابلة."""
        base_name = filename.replace("_ai", "").replace(".py", "")
        return ''.join([part.capitalize() for part in base_name.split('_')]) + "AI"

    for filename in os.listdir(strategies_path):
        if filename.endswith("_strategy_ai.py"):
            module_name = filename[:-3]  # إزالة ".py"
            module_path = f"{strategies_path}.{module_name}"
            
            # تحميل الملف كـ module
            try:
                strategy_module = importlib.import_module(module_path)
            except ModuleNotFoundError:
                print(f"تحذير: الملف {module_name} لم يتم تحميله بشكل صحيح.")
                continue
            
            # تحويل الاسم إلى CamelCase وإضافة AI
            class_name = convert_to_camel_case(filename)
            
            # الحصول على الفئة المناسبة وتحميلها
            try:
                strategy_class = getattr(strategy_module, class_name)
                strategies[class_name] = strategy_class
                print(f"تم تحميل الاستراتيجية: {class_name}")
            except AttributeError:
                print(f"تحذير: لم يتم العثور على الفئة {class_name} في الملف {filename}.")
    
    return strategies
