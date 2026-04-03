import time
import sys
import random
import json
import pandas as pd
from datetime import datetime
from faker import Faker

# Инициализация
fake = Faker()
# Хранилище для накопления данных в рамках сессии (для расчета метрики)
history = []

def generate_data():
    """Генерация одной записи продажи"""
    categories = ['Electronics', 'Apparel', 'Home', 'Beauty', 'Books']
    return {
        "order_id": fake.uuid4()[:8].upper(),
        "timestamp": datetime.now().strftime("%H:%M:%S"),
        "category": random.choice(categories) ,
        "amount": round(random.uniform(10, 1000), 2),
        "status": random.choice(["Completed", "Refunded"])
    }

def analyze_data(new_record):
    """Аналитическая часть: расчет среднего чека (AOV) по категориям"""
    global history
    history.append(new_record)
    
    # Превращаем накопленные данные в DataFrame для анализа
    df = pd.DataFrame(history)
    
    # Фильтруем только завершенные заказы (бизнес-логика)
    completed_orders = df[df['status'] == 'Completed']
    
    if not completed_orders.empty:
        # Расчет средней суммы по категориям
        aov_by_cat = completed_orders.groupby('category')['amount'].mean().round(2).to_dict()
        return aov_by_cat
    return {}

def main():
    print(f"[{datetime.now()}] Starting E-commerce Analytics Stream...", flush=True)
    
    try:
        while True:
            # 1. Генерация
            record = generate_data()
            
            # 2. Анализ (расчет метрики)
            current_metrics = analyze_data(record)
            
            # 3. Вывод результата в stdout (метка времени + JSON)
            output = {
                "event": record,
                "metrics_summary": {
                    "description": "Average Order Value by Category",
                    "values": current_metrics
                }
            }
            print(json.dumps(output, indent=None), flush=True)
            
            # Интервал 10 секунд по ТЗ
            time.sleep(10)
    except KeyboardInterrupt:
        sys.exit(0)

if __name__ == "__main__":
    main()