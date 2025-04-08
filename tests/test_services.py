import json
import unittest
from typing import Any
from unittest.mock import patch

import pandas as pd

from src.services import analyze_cashback_categories, search_transactions


class TestAnalyzeCashbackCategories(unittest.TestCase):

    @patch('pandas.read_excel')
    @patch('builtins.input', side_effect=['2021', '12'])
    def test_analyze_cashback_categories_success(self, mock_input: Any, mock_read_excel: Any) -> None:
        test_data = {
            'Дата операции': ['31.12.2021 16:44:00', '30.12.2021 10:00:00', '01.01.2022 12:00:00'],
            'Категория': ['Еда', 'Транспорт', 'Зарплата'],
            'Сумма операции': [-1000, -500, -2000]
        }
        df = pd.DataFrame(test_data)
        mock_read_excel.return_value = df

        result = analyze_cashback_categories()

        expected_result = json.dumps({'Еда': 10.0, 'Транспорт': 5.0}, ensure_ascii=False)
        self.assertEqual(result, expected_result)

    @patch('pandas.read_excel', side_effect=Exception("Ошибка чтения файла"))
    @patch('builtins.input', side_effect=['2021', '12'])
    def test_analyze_cashback_categories_file_read_error(self, mock_input: Any, mock_read_excel: Any) -> None:
        result = analyze_cashback_categories()

        expected_result = json.dumps({"error": "Ошибка чтения файла"}, ensure_ascii=False)
        self.assertEqual(result, expected_result)

    @patch('pandas.read_excel')
    @patch('builtins.input', side_effect=['2021', '12'])
    def test_analyze_cashback_categories_excluded_categories(self, mock_input: Any, mock_read_excel: Any) -> None:
        test_data = {
            'Дата операции': ['31.12.2021 16:44:00', '30.12.2021 10:00:00'],
            'Категория': ['Зарплата', 'Переводы'],
            'Сумма операции': [-1000, -500]
        }
        df = pd.DataFrame(test_data)
        mock_read_excel.return_value = df

        result = analyze_cashback_categories()

        expected_result = json.dumps({}, ensure_ascii=False)
        self.assertEqual(result, expected_result)


class TestSearchTransactions(unittest.TestCase):

    @patch('pandas.read_excel')
    def test_search_transactions_success(self, mock_read_excel: Any) -> None:
        test_data = {
            'Описание': ['Покупка в магазине', 'Оплата за услуги', 'Перевод другу'],
            'Категория': ['Еда', 'Коммунальные услуги', 'Переводы'],
            'Сумма операции': [-1000, -500, -200]
        }
        df = pd.DataFrame(test_data)
        mock_read_excel.return_value = df

        query = "магазин"
        result = search_transactions(query)

        expected_result = json.dumps({
            "transactions": [
                {"Описание": "Покупка в магазине", "Категория": "Еда", "Сумма операции": -1000}
            ]
        }, ensure_ascii=False)

        self.assertEqual(result, expected_result)

    @patch('pandas.read_excel', side_effect=Exception("Ошибка чтения файла"))
    def test_search_transactions_file_read_error(self, mock_read_excel: Any) -> None:
        query = "магазин"
        result = search_transactions(query)

        expected_result = json.dumps({"error": "Ошибка чтения файла"}, ensure_ascii=False)
        self.assertEqual(result, expected_result)

    @patch('pandas.read_excel')
    def test_search_transactions_no_results(self, mock_read_excel: Any) -> None:
        test_data = {
            'Описание': ['Покупка в магазине', 'Оплата за услуги'],
            'Категория': ['Еда', 'Коммунальные услуги'],
            'Сумма операции': [-1000, -500]
        }
        df = pd.DataFrame(test_data)
        mock_read_excel.return_value = df

        query = "неизвестный запрос"
        result = search_transactions(query)

        expected_result = json.dumps({"message": "Такого слова не было обнаружено."}, ensure_ascii=False)

        self.assertEqual(result, expected_result)

    def test_search_transactions_with_list_of_dicts_success(self) -> None:
        sample_transactions = [
            {"Описание": "Покупка в магазине", "Категория": "Еда", "Сумма операции": -1000},
            {"Описание": "Оплата за услуги", "Категория": "Коммунальные услуги", "Сумма операции": -500},
            {"Описание": "Перевод другу", "Категория": "Переводы", "Сумма операции": -200},
        ]

        query = "магазин"
        result = search_transactions(query, sample_transactions)

        expected_result = json.dumps({
            "transactions": [
                {"Описание": "Покупка в магазине", "Категория": "Еда", "Сумма операции": -1000}
            ]
        }, ensure_ascii=False)

        self.assertEqual(result, expected_result)
