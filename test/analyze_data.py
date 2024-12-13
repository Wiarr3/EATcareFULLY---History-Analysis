import unittest
import pandas as pd
from datetime import datetime
from collections import namedtuple
from src.analyze_data import (
    total_macros, list_days_with_deviation, calorie_stats, generate_dietary_advice
)

Preferences = namedtuple('Preferences', ['protein_threshold', 'fat_threshold', 'carbon_threshold', 'calorie_threshold'])

class AnalyzeDataTest(unittest.TestCase):
    def setUp(self):
        self.preferences = Preferences(
            protein_threshold=100,
            fat_threshold=70,
            carbon_threshold=250,
            calorie_threshold=2000
        )

        data = {
            'date': pd.date_range(start="2024-11-01", periods=30, freq='D'),
            'proteins_total': [100] * 30,
            'fat_total': [60] * 30,
            'carbohydrates_total': [240] * 30,
            'energy_kcal_total': [2000] * 30,
            'name': ['food'] * 30,
        }
        self.mock_dataframe = pd.DataFrame(data)

    def test_total_macros(self):
        protein_total, protein_daily_deviation, fat_total, fat_daily_deviation, carbs_total, carbs_daily_deviation = total_macros(
            self.mock_dataframe, self.preferences, month=11, year=2024
        )

        self.assertEqual(protein_total, 3000)
        self.assertEqual(fat_total, 1800)
        self.assertEqual(carbs_total, 7200)


    def test_list_days_with_deviation(self):
        high_deviation_days, low_deviation_days = list_days_with_deviation(
            self.mock_dataframe, macro='proteins_total', threshold=1.5
        )

        self.assertEqual(len(high_deviation_days), 0)
        self.assertEqual(len(low_deviation_days), 0)

    def test_calorie_stats(self):
        total_calories, std_calories, daily_calorie_deviation, weekly_calories_df = calorie_stats(
            self.mock_dataframe, self.preferences, month=11, year=2024
        )

        self.assertEqual(total_calories, 60000)
        self.assertEqual(len(weekly_calories_df), 5)

    def test_generate_dietary_advice(self):
        advice = generate_dietary_advice(self.mock_dataframe, self.preferences, month=11, year=2024)

        self.assertIn("you exceeded your daily caloric limit", advice)
        self.assertIn("macronutrient balance was", advice)
        self.assertIn("Ideally, your diet should consist of approximately 50% carbohydrates, 25% protein, and 25% fat.", advice)


if __name__ == '__main__':
    unittest.main()
