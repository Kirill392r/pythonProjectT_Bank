import json
import os
from typing import Any

from dotenv import load_dotenv

from src.reports import spending_by_category
from src.services import analyze_cashback_categories, search_transactions
from src.utils import get_file_paths, read_operations_data
from src.views import base_func_module_one

load_dotenv()

EXCHANGE_RATES_API_KEY = os.getenv("EXCHANGE_RATES_API_KEY")
ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")


def main() -> None:
    """
    Царь-функция - здесь нет ничего особенного, она просто
    объединяет функционал из разных модулей
    """
    settings_file_path: str
    excel_file_path: str
    settings_file_path, excel_file_path = get_file_paths()

    df: Any = read_operations_data(excel_file_path)
    date_str = input("Введите дату (например, '2020-05-02 20:00:00'): ")
    print(base_func_module_one(date_str))

    cashback_result = analyze_cashback_categories()
    print("Анализ кешбэка:", cashback_result)

    query: str = input("Введите слово для поиска в транзакциях: ")

    search_result = search_transactions(query)
    print("Результаты поиска транзакций:", search_result)

    category: str = input("Введите категорию для анализа расходов:")

    year: int = int(input("Введите год (например, 2020): "))

    month: int = int(input("Введите месяц (1-12): "))

    spending_result = spending_by_category(df, category, year, month)

    print("Расходы по категории:", json.dumps(spending_result, ensure_ascii=False))


if __name__ == "__main__":
    main()
