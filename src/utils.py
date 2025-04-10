import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, Hashable, List, Tuple

import pandas as pd
import requests

# Настройка логирования
logging.basicConfig(level=logging.INFO)


def read_operations_data(file_path: str) -> pd.DataFrame:
    """Чтение данных из Excel файла"""
    df = pd.read_excel(file_path)
    # Преобразование столбца 'Дата операции' в формат datetime
    df["Дата операции"] = pd.to_datetime(df["Дата операции"], errors="coerce", dayfirst=True)
    return df


def get_greeting(current_time: datetime) -> str:
    """Получение приветствия в зависимости от времени суток"""
    if current_time.hour < 6:
        return "Доброй ночи"
    elif current_time.hour < 12:
        return "Доброе утро"
    elif current_time.hour < 18:
        return "Добрый день"
    else:
        return "Добрый вечер"


def process_card_data(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """Обработка данных по картам."""
    card_data = df["Номер карты"].dropna().unique()
    result = []

    for card in card_data:
        card_transactions = df[df["Номер карты"] == card]
        total_spent = card_transactions["Сумма операции"].sum()
        cashback = total_spent / -100  # 1 рубль на каждые 100 рублей

        result.append({"last_digits": card[-4:], "total_spent": round(total_spent, 2), "cashback": round(cashback, 2)})

    return result


def get_top_transactions(df: pd.DataFrame) -> list[dict[Hashable, Any]]:
    """Получение топ-5 транзакций по сумме платежа."""
    top_transactions = df.nlargest(5, "Сумма платежа")[["Дата операции", "Сумма платежа", "Категория", "Описание"]]
    top_transactions["Дата операции"] = top_transactions["Дата операции"].dt.strftime("%d.%m.%Y")

    # Убедимся, что все ключи являются строками
    return top_transactions.to_dict(orient="records")


def get_currency_rates(api_key: str) -> List[Dict[str, float]]:
    """Получение курсов валют"""
    url = "https://api.apilayer.com/exchangerates_data/latest"
    headers = {"apikey": api_key}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        return [{"currency": currency, "rate": float(rate)} for currency, rate in data["rates"].items()]
    else:
        logging.error(f"Ошибка при получении курсов валют: {response.status_code} - {response.text}")
        return []


def get_stock_prices(api_key: str, stocks: List[str]) -> list[dict[str, object]]:
    """Получение цен акций"""
    stock_prices = []

    for stock in stocks:
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={stock}&interval=1min&apikey={api_key}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            if "Time Series (1min)" in data:
                latest_time = next(iter(data["Time Series (1min)"]))
                price = float(data["Time Series (1min)"][latest_time]["1. open"])
                stock_prices.append({"stock": stock, "price": round(price, 2)})
            else:
                logging.error(f"Ключ 'Time Series (1min)' отсутствует для {stock}. Ответ: {data}")
        else:
            logging.error(f"Ошибка при получении цены акций {stock}: {response.status_code}")

    return stock_prices


def load_user_settings(file_path: str) -> Dict[str, List[str]]:
    """Загрузка пользовательских настроек из JSON файла"""
    try:
        with open(file_path) as f:
            data: Any = json.load(f)  # Загружаем данные как Any
            # Приводим к нужному типу
            return {"user_stocks": data.get("user_stocks", [])}
    except FileNotFoundError:
        logging.error("Файл user_settings.json не найден. Используйте значения по умолчанию.")
        return {"user_stocks": []}  # Возвращаем пустой список акций по умолчанию


def get_file_paths() -> Tuple[str, str]:
    """Определяет пути к файлам настроек и операциям"""
    settings_file_path = os.path.join(os.path.dirname(__file__), "../user_settings.json")
    excel_file_path = os.path.join(os.path.dirname(__file__), "../data/operations.xlsx")
    return settings_file_path, excel_file_path


def parse_date(date_str: str) -> datetime:
    """Преобразует строку даты в объект datetime"""
    return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
