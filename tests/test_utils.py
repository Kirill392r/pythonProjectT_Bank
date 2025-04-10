from datetime import datetime
from unittest.mock import MagicMock, mock_open, patch

import pandas as pd
import pytest

from src.utils import (get_currency_rates, get_file_paths, get_greeting, get_stock_prices, get_top_transactions,
                       load_user_settings, parse_date, process_card_data)


@pytest.fixture
def sample_df():
    data = {
        "Дата операции": pd.to_datetime(
            ["2023-01-01 10:00:00", "2023-01-02 11:00:00", "2023-01-03 12:00:00", "2023-01-04 13:00:00"]
        ),
        "Номер карты": ["1234567890123456", "1234567890123456", "9876543210987654", None],
        "Сумма операции": [-1000, -2000, -1500, -500],
        "Сумма платежа": [-1000, -2000, -1500, -500],
        "Категория": ["Еда", "Транспорт", "Развлечения", "Еда"],
        "Описание": ["Магазин", "Такси", "Кино", "Ресторан"],
    }
    return pd.DataFrame(data)


@pytest.mark.parametrize(
    "hour,expected", [(3, "Доброй ночи"), (8, "Доброе утро"), (14, "Добрый день"), (20, "Добрый вечер")]
)
def test_get_greeting(hour, expected):
    assert get_greeting(datetime(2023, 1, 1, hour)) == expected


# Тесты для process_card_data
def test_process_card_data(sample_df):
    result = process_card_data(sample_df)
    assert len(result) == 2
    assert result[0]["last_digits"] == "3456"
    assert result[0]["total_spent"] == -3000.0


# Тесты для get_top_transactions
def test_get_top_transactions(sample_df):
    result = get_top_transactions(sample_df)
    assert len(result) == 4
    assert result[0]["Сумма платежа"] == -500


# Тесты для parse_date
def test_parse_date_valid():
    assert parse_date("2023-01-01 12:00:00") == datetime(2023, 1, 1, 12)


def test_parse_date_invalid():
    with pytest.raises(ValueError):
        parse_date("invalid-date")


# Тесты для load_user_settings
def test_load_user_settings_valid():
    mock_data = '{"user_stocks": ["AAPL", "GOOGL"]}'
    with patch("builtins.open", mock_open(read_data=mock_data)):
        result = load_user_settings("dummy_path")
        assert result["user_stocks"] == ["AAPL", "GOOGL"]


def test_load_user_settings_file_not_found():
    with patch("builtins.open", side_effect=FileNotFoundError):
        result = load_user_settings("dummy_path")
        assert result["user_stocks"] == []


# Тесты для API функций
def test_get_currency_rates_success():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"rates": {"USD": 1.0}}

    with patch("requests.get", return_value=mock_response):
        result = get_currency_rates("dummy_key")
        assert len(result) > 0


def test_get_stock_prices_success():
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"Time Series (1min)": {"2023-01-01 12:00:00": {"1. open": "150.0"}}}

    with patch("requests.get", return_value=mock_response):
        result = get_stock_prices("dummy_key", ["AAPL"])
        assert len(result) == 1


# Тесты для get_file_paths
def test_get_file_paths():
    with patch("os.path.dirname", return_value="/dummy/path"):
        settings, excel = get_file_paths()
        assert "user_settings.json" in settings
        assert "operations.xlsx" in excel
