import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
from datetime import datetime
from src.process_data import process_data
from src.utils import ProductEntry

class ProcessDataTest(unittest.TestCase):

    def setUp(self):
        self.product_entries = MagicMock()
        self.product_entries.products = [
            ProductEntry(code="1234567890123", date=datetime(2024, 11, 1), quantity=2),
            ProductEntry(code="9876543210987", date=datetime(2024, 11, 2), quantity=1),
        ]

    @patch("src.process_data.get_product_with_retry")
    def test_process_data_with_valid_products(self, mock_get_product):
        mock_get_product.side_effect = [
            {
                "product_name": "Mock Product 1",
                "nutriments": {
                    "energy-kcal_100g": 200,
                    "fat_100g": 10,
                    "saturated-fat_100g": 3,
                    "carbohydrates_100g": 30,
                    "sugars_100g": 20,
                    "proteins_100g": 5,
                    "salt_100g": 0.5,
                },
                "quantity": "500g",
                "nutriscore_grade": "a",
                "categories": "Snacks, Sweet snacks",
            },
            {
                "product_name": "Mock Product 2",
                "nutriments": {
                    "energy-kcal_100g": 150,
                    "fat_100g": 5,
                    "saturated-fat_100g": 2,
                    "carbohydrates_100g": 25,
                    "sugars_100g": 15,
                    "proteins_100g": 10,
                    "salt_100g": 0.3,
                },
                "quantity": "250g",
                "nutriscore_grade": "b",
                "categories": "Beverages, Soft drinks",
            },
        ]

        result_df = process_data(self.product_entries)

        self.assertEqual(len(result_df), 3)
        self.assertIn("id", result_df.columns)
        self.assertIn("name", result_df.columns)
        self.assertIn("energy_kcal_total", result_df.columns)
        self.assertEqual(result_df["name"].iloc[0], "Mock Product 1")

        self.assertAlmostEqual(result_df["energy_kcal_total"].iloc[0], 1000)
        self.assertAlmostEqual(result_df["proteins_total"].iloc[0], 25)

    @patch("src.process_data.get_product_with_retry")
    def test_process_data_with_missing_product(self, mock_get_product):
        mock_get_product.side_effect = [
            {
                "product_name": "Mock Product 1",
                "nutriments": {
                    "energy-kcal_100g": 200,
                    "fat_100g": 10,
                    "saturated-fat_100g": 3,
                    "carbohydrates_100g": 30,
                    "sugars_100g": 20,
                    "proteins_100g": 5,
                    "salt_100g": 0.5,
                },
                "quantity": "500g",
                "nutriscore_grade": "a",
                "categories": "Snacks, Sweet snacks",
            },
            None,
        ]

        result_df = process_data(self.product_entries)

        self.assertEqual(len(result_df), 2)
        self.assertIn("name", result_df.columns)
        self.assertEqual(result_df["name"].iloc[0], "Mock Product 1")

    @patch("src.process_data.get_product_with_retry")
    def test_process_data_with_invalid_quantity(self, mock_get_product):
        mock_get_product.return_value = {
            "product_name": "Mock Product 1",
            "nutriments": {
                "energy-kcal_100g": 200,
                "fat_100g": 10,
                "saturated-fat_100g": 3,
                "carbohydrates_100g": 30,
                "sugars_100g": 20,
                "proteins_100g": 5,
                "salt_100g": 0.5,
            },
            "quantity": "N/A",
            "nutriscore_grade": "a",
            "categories": "Snacks, Sweet snacks",
        }

        result_df = process_data(self.product_entries)

        self.assertAlmostEqual(result_df["energy_kcal_total"].iloc[0], 200)
        self.assertAlmostEqual(result_df["proteins_total"].iloc[0], 5)

if __name__ == "__main__":
    unittest.main()
