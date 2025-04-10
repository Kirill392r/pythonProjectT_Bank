import json
import os
from datetime import datetime
from typing import Any, Dict

from dotenv import load_dotenv

from src.utils import (get_currency_rates, get_file_paths, get_greeting, get_stock_prices, get_top_transactions,
                       load_user_settings, parse_date, process_card_data, read_operations_data)

# Загрузка переменных окружения из .env файла
load_dotenv()

EXCHANGE_RATES_API_KEY = os.getenv("APY_KEY_CURRENCY_RATES")
ALPHA_VANTAGE_API_KEY = os.getenv("APY_KEY_STOCK_PRICES")


def base_func_module_one(date_str: str) -> str:
    """Основная функция страницы «Главная», тянет данные с utils.py"""

    # Получаем пути к файлам
    settings_file_path, excel_file_path = get_file_paths()

    # Загружаем пользовательские настройки
    user_settings = load_user_settings(settings_file_path)

    stocks_to_check = user_settings.get("user_stocks", [])

    # Чтение данных операций
    df = read_operations_data(excel_file_path)

    # Преобразование строки даты в объект datetime
    input_date = parse_date(date_str)

    # Получаем данные за текущий месяц до указанной даты
    start_date = input_date.replace(day=1)

    filtered_df = df[(df["Дата операции"] >= start_date) & (df["Дата операции"] <= input_date)]

    # Получаем текущее время для приветствия
    current_time = datetime.now()

    greeting = get_greeting(current_time)

    cards_info = process_card_data(filtered_df)

    top_transactions_info = get_top_transactions(filtered_df)

    # Проверяем наличие API ключей перед вызовом функций
    if EXCHANGE_RATES_API_KEY is None:
        raise ValueError("EXCHANGE_RATES_API_KEY не установлен.")

    currency_rates_info = get_currency_rates(EXCHANGE_RATES_API_KEY)

    if ALPHA_VANTAGE_API_KEY is None:
        raise ValueError("ALPHA_VANTAGE_API_KEY не установлен.")

    stock_prices_info = get_stock_prices(ALPHA_VANTAGE_API_KEY, stocks_to_check)

    response_json: Dict[str, Any] = {
        "greeting": greeting,
        "cards": cards_info,
        "top_transactions": top_transactions_info,
        "currency_rates": currency_rates_info,
        "stock_prices": stock_prices_info,
    }

    return json.dumps(response_json, ensure_ascii=False, indent=4)


# Пример вызова функции main
if __name__ == "__main__":
    print(base_func_module_one("2020-05-02 20:00:00"))
