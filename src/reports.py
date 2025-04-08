import json
import logging
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, Optional

import pandas as pd

# Настройка логирования
logging.basicConfig(level=logging.INFO)


def log_report_result(func: Callable[..., Dict[str, Any]]) -> Callable[..., Dict[str, Any]]:
    """
    Декоратор для логирования результата выполнения функции и записи его в JSON-файл.
    """
    def wrapper(*args: Any, **kwargs: Any) -> Dict[str, Any]:
        result = func(*args, **kwargs)
        # Определяем имя файла для записи результата
        filename = kwargs.get('filename', 'spending_report.json')

        # Записываем результат в файл с ensure_ascii=False
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False)

        logging.info(f'Result written to {filename}')
        return result

    return wrapper


@log_report_result
def spending_by_category(transactions: pd.DataFrame,
                         category: str,
                         year: Optional[int] = None,
                         month: Optional[int] = None,
                         day: Optional[int] = None) -> Dict[str, Any]:
    """
    Вычисляет общие траты по заданной категории за последние три месяца до указанной даты.
    Если год, месяц или день не указаны, запрашивает их у пользователя.
    """

    # Запрос года, месяца и дня у пользователя, если они не указаны
    if year is None or month is None or day is None:
        if year is None:
            year = int(input("Введите год (например, 2020): "))
        if month is None:
            month = int(input("Введите месяц (1-12): "))
        if day is None:
            day = int(input("Введите день (1-31): "))

    # Создаем дату на основе введенного года, месяца и дня
    date = datetime(year, month, day)

    # Определяем дату три месяца назад
    three_months_ago = date - timedelta(days=90)

    # Преобразуем столбец 'Дата операции' в формат datetime
    transactions['Дата операции'] = pd.to_datetime(transactions['Дата операции'], format='%d.%m.%Y %H:%M:%S',
                                                   errors='coerce')

    # Фильтруем транзакции по категории и дате (включая верхнюю границу)
    filtered_transactions = transactions[
        (transactions['Категория'] == category) &
        (transactions['Дата операции'] >= three_months_ago) &
        (transactions['Дата операции'] <= date + timedelta(days=1))
        ]

    # Суммируем траты по выбранной категории (используем абсолютное значение суммы)
    total_spending = float(filtered_transactions['Сумма операции'].sum())

    return {
        'category': category,
        'total_spending': total_spending,
        'date': date.strftime('%Y-%m-%d')
    }
