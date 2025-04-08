from datetime import datetime

import pandas as pd
import pytest
from pytest_mock import MockerFixture

from src.utils import (get_greeting, get_top_transactions, load_user_settings, parse_date, process_card_data,
                       read_operations_data)


# Тестовые данные
@pytest.fixture
def sample_data() -> pd.DataFrame:
    """Создание тестового DataFrame для операций."""
    data = {
        'Дата операции': [
            '2023-01-01 10:00:00',
            '2023-01-02 11:00:00',
            '2023-01-03 12:00:00',
            '2023-01-04 13:00:00',
            '2023-01-05 14:00:00'
        ],
        'Номер карты': ['1234567890123456', '1234567890123456', '9876543210987654', None, '1234567890123456'],
        'Сумма операции': [-1000, -2000, -1500, -500, -3000],
        'Сумма платежа': [-1000, -2000, -1500, -500, -3000],
        'Категория': ['Еда', 'Транспорт', 'Развлечения', 'Еда', 'Транспорт'],
        'Описание': ['Покупка в магазине', 'Поездка на такси', 'Билет в кино', 'Ужин в ресторане',
                     'Поездка на автобусе']
    }
    df = pd.DataFrame(data)
    df['Дата операции'] = pd.to_datetime(df['Дата операции'])
    return df


def test_get_greeting() -> None:
    """Тестирование функции получения приветствия."""
    assert get_greeting(datetime(2023, 1, 1, 5)) == "Доброй ночи"
    assert get_greeting(datetime(2023, 1, 1, 10)) == "Доброе утро"
    assert get_greeting(datetime(2023, 1, 1, 15)) == "Добрый день"
    assert get_greeting(datetime(2023, 1, 1, 19)) == "Добрый вечер"


def test_process_card_data(sample_data: pd.DataFrame) -> None:
    """Тестирование обработки данных по картам."""
    result = process_card_data(sample_data)

    assert len(result) == 2
    assert result[0]['last_digits'] == "3456"
    assert result[0]['total_spent'] == round(-6000.0, 2)
    assert result[0]['cashback'] == round(60.0, 2)


def test_get_top_transactions(sample_data: pd.DataFrame) -> None:
    """Тестирование получения топ-транзакций."""
    result = get_top_transactions(sample_data)

    assert len(result) == 5
    assert result[0]['Сумма платежа'] == -500
    assert result[1]['Сумма платежа'] == -1000


def test_parse_date() -> None:
    """Тестирование преобразования строки даты в объект datetime."""
    date_str = "2023-01-01 12:00:00"
    parsed_date = parse_date(date_str)

    assert parsed_date == datetime(2023, 1, 1, 12)


def test_load_user_settings(mocker: MockerFixture) -> None:
    """Тестирование загрузки пользовательских настроек."""

    mock_open = mocker.patch("builtins.open", mocker.mock_open(read_data='{"user_stocks": ["AAPL", "GOOGL"]}'))

    settings = load_user_settings("dummy_path")

    assert settings["user_stocks"] == ["AAPL", "GOOGL"]


def test_load_user_settings_file_not_found(mocker: MockerFixture) -> None:
    """Тестирование загрузки пользовательских настроек при отсутствии файла."""

    mock_open = mocker.patch("builtins.open", side_effect=FileNotFoundError)

    settings = load_user_settings("dummy_path")

    assert settings["user_stocks"] == []


def test_read_operations_data_invalid_file() -> None:
    """Тестирование функции read_operations_data при отсутствии файла."""

    with pytest.raises(FileNotFoundError):
        read_operations_data("dummy_path.xlsx")