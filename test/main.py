import os
import unittest
from datetime import datetime
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

from src.main import app, ProductReportGenerator, AnalyzeProductsRequest

class TestAPI(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

        # Mock input data
        self.request_data = {
            "month": 11,
            "year": 2024,
            "preferences": {
                "calorie_threshold": 2000,
                "protein_threshold": 100,
                "carbon_threshold": 250,
                "fat_threshold": 70,
            },
            "products": [
                {"code": "1234567890123", "date": "2024-11-01T00:00:00", "quantity": 2},
                {"code": "9876543210987", "date": "2024-11-02T00:00:00", "quantity": 1},
            ],
        }

    @patch("src.main.ProductReportGenerator.generate_pdf_report")
    @patch("src.main.ProductReportGenerator.__init__", return_value=None)
    def test_analyze_products_success(self, mock_init, mock_generate_report):
        mock_generate_report.return_value = None

        unique_id = "test-uuid"
        with patch("uuid.uuid4", return_value=unique_id), patch("os.path.exists", return_value=True):
            response = self.client.post("/analyze/", json=self.request_data)

        self.assertEqual(response.status_code, 200)
        self.assertIn("application/pdf", response.headers["content-type"])
        self.assertIn(f"{unique_id}_report.pdf", response.headers["content-disposition"])

    @patch("os.path.exists", return_value=False)
    def test_analyze_products_pdf_not_found(self, mock_exists):
        response = self.client.post("/analyze/", json=self.request_data)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "PDF file not found")

    def test_root_endpoint(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"It works"})

if __name__ == "__main__":
    unittest.main()
