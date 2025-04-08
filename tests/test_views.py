import json
from unittest.mock import patch

import pandas as pd

from src.views import base_func_module_one

mock_user_settings = {
    "user_stocks": ["AAPL", "GOOGL"]
}

mock_operations_data = {
    'Дата операции': pd.to_datetime(['2021-12-31 16:44:00', '2021-12-31 16:42:04']),
    'Сумма операции': [-160.89, -64.00]
}
mock_filtered_df = pd.DataFrame(mock_operations_data)


def test_base_func_module_one_success() -> None:
    """Тестирование успешного выполнения функции base_func_module_one."""

    with patch('src.views.get_file_paths') as mock_get_file_paths, \
            patch('src.views.load_user_settings', return_value=mock_user_settings), \
            patch('src.views.read_operations_data', return_value=mock_filtered_df), \
            patch('src.views.parse_date', return_value=pd.to_datetime('2021-12-31')), \
            patch('src.views.get_greeting', return_value="Доброе утро!"), \
            patch('src.views.process_card_data', return_value={"card_info": "some_info"}), \
            patch('src.views.get_top_transactions', return_value={"top_transactions": "some_transactions"}), \
            patch('src.views.get_currency_rates', return_value={"USD": 73.0}), \
            patch('src.views.get_stock_prices', return_value={"AAPL": 150.0}):
        mock_get_file_paths.return_value = ("settings.json", "operations.xlsx")

        result = base_func_module_one("31.12.2021")

        expected_response = {
            "greeting": "Доброе утро!",
            "cards": {"card_info": "some_info"},
            "top_transactions": {"top_transactions": "some_transactions"},
            "currency_rates": {"USD": 73.0},
            "stock_prices": {"AAPL": 150.0},
        }

        assert result == json.dumps(expected_response, ensure_ascii=False)


def test_base_func_module_one_no_operations() -> None:
    """Тестирование функции base_func_module_one при отсутствии операций."""

    with patch('src.views.get_file_paths') as mock_get_file_paths, \
            patch('src.views.load_user_settings', return_value=mock_user_settings), \
            patch('src.views.read_operations_data',
                  return_value=pd.DataFrame(columns=['Дата операции', 'Сумма операции'])), \
            patch('src.views.parse_date', return_value=pd.to_datetime('2021-12-31')), \
            patch('src.views.get_greeting', return_value="Доброе утро!"), \
            patch('src.views.process_card_data', return_value={}), \
            patch('src.views.get_top_transactions', return_value={}), \
            patch('src.views.get_currency_rates', return_value={}), \
            patch('src.views.get_stock_prices', return_value=[]):
        mock_get_file_paths.return_value = ("settings.json", "operations.xlsx")

        result = base_func_module_one("31.12.2021")

        expected_response = {
            "greeting": "Доброе утро!",
            "cards": {},
            "top_transactions": {},
            "currency_rates": {},
            "stock_prices": [],
        }

        assert result == json.dumps(expected_response, ensure_ascii=False)