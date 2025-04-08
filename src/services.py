import json
import logging
import os
from datetime import datetime

import pandas as pd

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

FILE_PATH = os.path.join(os.path.dirname(__file__), '../data/operations.xlsx')

EXCLUDED_CATEGORIES = ['Зарплата', 'Переводы', 'Пополнения']


def analyze_cashback_categories() -> str:
    """
    Запрашивает год и месяц для анализа, анализирует суммы кешбэка по категориям на основе данных из Excel,
    исключая заранее определенные категории.
    """

    year = int(input("Введите год для анализа CashBack (например, 2021): "))
    month = int(input("Введите месяц для анализа CashBack (например, 12): "))

    logging.info(f"Начинаем анализ кешбэка за {month}/{year}")

    try:
        data = pd.read_excel(FILE_PATH)
        logging.info("Данные успешно загружены из Excel.")
    except Exception as e:
        logging.error(f"Ошибка при чтении файла Excel: {str(e)}")
        return json.dumps({"error": str(e)}, ensure_ascii=False)  # Убедитесь, что здесь установлен ensure_ascii=False

    data['Дата операции'] = pd.to_datetime(data['Дата операции'], format='%d.%m.%Y %H:%M:%S')

    start_date = datetime(year, month, 1)

    if month == 12:
        end_date = datetime(year + 1, 1, 1)
    else:
        end_date = datetime(year, month + 1, 1)

    filtered_data = data[(data['Дата операции'] >= start_date) & (data['Дата операции'] < end_date)]

    logging.info(f"Количество транзакций за указанный период: {len(filtered_data)}")

    filtered_data = filtered_data[~filtered_data['Категория'].isin(EXCLUDED_CATEGORIES)]

    logging.info(f"Исключены категории: {EXCLUDED_CATEGORIES}. Осталось транзакций: {len(filtered_data)}")

    cashback_summary = filtered_data.groupby('Категория')['Сумма операции'].sum().abs() / 100

    top_categories = cashback_summary.nlargest(3).to_dict()

    logging.info(f"Топ-3 категорий по кешбеку: {top_categories}")

    result_json = json.dumps(top_categories, ensure_ascii=False)

    return result_json



logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def search_transactions(query: str, transactions: list[dict] | None = None) -> str:
    """
    Ищет транзакции по запросу в описании или категории.
    """

    if transactions is None:
        try:
            data = pd.read_excel(FILE_PATH)
            logging.info("Данные успешно загружены из Excel.")
        except Exception as e:
            logging.error(f"Ошибка при чтении файла Excel: {str(e)}")
            return json.dumps({"error": str(e)}, ensure_ascii=False)
    else:
        # Преобразуем список словарей в DataFrame
        data = pd.DataFrame(transactions)

    # Фильтрация данных по запросу
    filtered_data = data[data['Описание'].str.contains(query, case=False, na=False) |
                         data['Категория'].str.contains(query, case=False, na=False)]

    if not filtered_data.empty:
        logging.info(f"Найдено {len(filtered_data)} транзакций по запросу '{query}'.")
        result_json = {
            "transactions": json.loads(filtered_data.to_json(orient='records', force_ascii=False))
        }
        return json.dumps(result_json, ensure_ascii=False)
    else:
        logging.info(f"По запросу '{query}' ничего не найдено.")
        return json.dumps({"message": "Такого слова не было обнаружено."}, ensure_ascii=False)
