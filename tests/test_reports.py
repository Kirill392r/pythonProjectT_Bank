import unittest
from unittest.mock import patch

import pandas as pd

from src.reports import spending_by_category


class TestSpendingByCategory(unittest.TestCase):

    def setUp(self) -> None:
        data = {
            'Категория': ['Еда', 'Транспорт', 'Еда', 'Развлечения', 'Еда'],
            'Дата операции': [
                '01.01.2023 12:00:00',
                '15.01.2023 12:00:00',
                '20.02.2023 12:00:00',
                '10.03.2023 12:00:00',
                '25.03.2023 12:00:00'
            ],
            'Сумма операции': [-1000, -500, -1500, -2000, -800]
        }
        self.transactions = pd.DataFrame(data)

    def test_spending_by_category_valid(self) -> None:
        result = spending_by_category(self.transactions, category='Еда', year=2023, month=3, day=31)
        self.assertEqual(result['category'], 'Еда')
        self.assertEqual(result['total_spending'], -3300)  # Сумма трат по категории "Еда"
        self.assertEqual(result['date'], '2023-03-31')

    def test_spending_by_category_no_transactions(self) -> None:
        result = spending_by_category(self.transactions, category='Техника', year=2023, month=3, day=31)
        self.assertEqual(result['category'], 'Техника')
        self.assertEqual(result['total_spending'], 0)  # Нет трат по категории "Техника"
        self.assertEqual(result['date'], '2023-03-31')

    def test_spending_by_category_with_default_date(self) -> None:
        result = spending_by_category(self.transactions, category='Еда', year=2023, month=3, day=31)

        self.assertEqual(result['category'], 'Еда')
        self.assertEqual(result['total_spending'], -3300)

    def test_spending_by_category_invalid_date_format(self) -> None:
        with patch('builtins.input', side_effect=['2023', '3', 'invalid-day']):
            with self.assertRaises(ValueError):
                spending_by_category(self.transactions, category='Еда')