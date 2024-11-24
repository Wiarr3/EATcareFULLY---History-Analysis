import uuid
import os
from fpdf import FPDF
from analyze_data import plot_calorie_consumption_over_time, plot_macros, plot_calorie_limit_bar, plot_nutriscore, \
    calorie_stats, total_macros, top_caloric_products, weekly_macros_stats, top_macro_products
from process_data import process_data
from dataclasses import dataclass
import random
from datetime import datetime, timedelta
import pandas as pd


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PDF_DIR = os.path.join(BASE_DIR, "pdf")
JPG_DIR = os.path.join(BASE_DIR, "jpg")

class ProductReportGenerator:
    def __init__(self, product_entries, unique_id, month, year=datetime.now().year):
        self.product_entries = product_entries
        self.month = month
        self.year = year
        self.df = self.filter_data_by_month(process_data(self.product_entries))
        self.unique_id = unique_id

    def filter_data_by_month(self, df):
        df['date'] = pd.to_datetime(df['date'])
        monthly_df = df[(df['date'].dt.month == self.month) & (df['date'].dt.year == self.year)]
        return monthly_df

    def get_image_path(self, filename):
        return os.path.join(JPG_DIR, f"{self.unique_id}_{filename}")

    def get_pdf_path(self, filename):
        return os.path.join(PDF_DIR, f"{self.unique_id}_{filename}")

    def add_section_title(self, pdf, title):
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, title, ln=True, align="L")
        pdf.ln(5)

    def add_subsection_title(self, pdf, subtitle):
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, subtitle, ln=True, align="L")
        pdf.ln(3)

    def add_top_macro_products_table(self, pdf, top_macro_df, macro_name, macro_column):
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, f"Top {macro_name} Products", ln=True, align="L")
        pdf.set_font("Arial", "", 10)
        pdf.ln(5)

        pdf.cell(100, 10, "Product Name", border=1)
        pdf.cell(50, 10, f"{macro_name} Consumed (g)", border=1)
        pdf.cell(40, 10, "Percentage (%)", border=1)
        pdf.ln()

        for index, row in top_macro_df.iterrows():
            pdf.cell(100, 10, row['name'], border=1)
            pdf.cell(50, 10, f"{row[macro_column]:.2f}", border=1)
            pdf.cell(40, 10, f"{row['Percentage']}%", border=1)
            pdf.ln()

    def add_weekly_calories_table(self, pdf, weekly_calories_df):
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Weekly Calorie Consumption", ln=True, align="L")
        pdf.set_font("Arial", "", 10)
        pdf.ln(5)

        pdf.cell(50, 10, "Week Start", border=1)
        pdf.cell(50, 10, "Calories", border=1)
        pdf.ln()

        for index, row in weekly_calories_df.iterrows():
            pdf.cell(50, 10, row['Week Start'].strftime('%Y-%m-%d'), border=1)
            pdf.cell(50, 10, f"{row['Calories']:.2f}", border=1)
            pdf.ln()

    def add_weekly_macros_table(self, pdf, weekly_macros_df):
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Weekly Macronutrient Consumption", ln=True, align="L")
        pdf.set_font("Arial", "", 10)
        pdf.ln(5)

        pdf.cell(50, 10, "Week Start", border=1)
        pdf.cell(40, 10, "Protein (g)", border=1)
        pdf.cell(50, 10, "Carbohydrates (g)", border=1)
        pdf.cell(40, 10, "Fat (g)", border=1)
        pdf.ln()

        for index, row in weekly_macros_df.iterrows():
            pdf.cell(50, 10, row['Week Start'].strftime('%Y-%m-%d'), border=1)
            pdf.cell(40, 10, f"{row['Protein (g)']:.2f}", border=1)
            pdf.cell(50, 10, f"{row['Carbohydrates (g)']:.2f}", border=1)
            pdf.cell(40, 10, f"{row['Fat (g)']:.2f}", border=1)
            pdf.ln()

    def add_top_caloric_products_table(self, pdf, top_caloric_df):
        pdf.set_font("Arial", "B", 12)
        pdf.cell(0, 10, "Top Caloric Products", ln=True, align="L")
        pdf.set_font("Arial", "", 10)
        pdf.ln(5)

        pdf.cell(100, 10, "Product Name", border=1)
        pdf.cell(50, 10, "Calories Consumed", border=1)
        pdf.ln()

        for product_name, calories in top_caloric_df.items():
            pdf.cell(100, 10, product_name, border=1)
            pdf.cell(50, 10, f"{calories:.2f}", border=1)
            pdf.ln()

    def generate_pdf_report(self):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 12)

        pdf.cell(0, 10, f"Diet Analysis Report for {self.month}-{self.year}", align="C", ln=True)
        pdf.ln(10)

        self.add_section_title(pdf, "Calorie Analysis")
        total_calories, std_calories, weekly_calories_df = calorie_stats(self.df, self.month, self.year)

        pdf.set_font("Arial", "", 10)
        pdf.cell(0, 10, f"Total Calorie Consumption: {total_calories:.2f} kcal", ln=True)
        pdf.cell(0, 10, f"Calorie Consumption Standard Deviation: {std_calories:.2f} kcal", ln=True)
        pdf.ln(5)

        self.add_weekly_calories_table(pdf, weekly_calories_df)
        pdf.ln(10)

        calories_image_path = self.get_image_path("calories_over_time.png")
        limits_image_path = self.get_image_path("calorie_limits.png")

        plot_calorie_consumption_over_time(self.df, freq='D', filename=calories_image_path)
        pdf.image(calories_image_path, x=10, y=170, w=180)
        pdf.ln(90)

        plot_calorie_limit_bar(self.df, freq='D', filename=limits_image_path)
        pdf.add_page()
        pdf.image(limits_image_path, x=10, y=30, w=180)
        pdf.ln(130)

        top_caloric_df = top_caloric_products(self.df)
        self.add_top_caloric_products_table(pdf, top_caloric_df)
        pdf.ln(10)

        pdf.add_page()
        self.add_section_title(pdf, "Macronutrient Analysis")
        protein_total, fat_total, carbs_total = total_macros(self.df)

        weekly_macros_df = weekly_macros_stats(self.df, self.month, self.year)
        self.add_weekly_macros_table(pdf, weekly_macros_df)
        pdf.ln(10)

        macros_combined_path = self.get_image_path("macros_combined.png")
        macros_prefix = self.get_image_path("macros")
        plot_macros(self.df, freq='D', filename_prefix=macros_prefix)
        pdf.image(macros_combined_path, x=10, y=120, w=180)
        pdf.ln(90)

        macro_totals = {
            'fat_total': fat_total,
            'carbohydrates_total': carbs_total,
            'proteins_total': protein_total
        }

        for macro, macro_name in zip(['fat_total', 'carbohydrates_total', 'proteins_total'],
                                     ['Fat', 'Carbohydrates', 'Protein']):
            pdf.add_page()
            self.add_subsection_title(pdf, f"{macro_name} Analysis")
            pdf.cell(0, 10, f"Total {macro_name} Consumption: {macro_totals[macro]:.2f}g", ln=True)
            pdf.ln(5)

            macro_image_path = self.get_image_path(f"macros_{macro}.png")
            pdf.image(macro_image_path, x=10, y=30, w=180)
            pdf.ln(90)

            top_macro_df = top_macro_products(self.df, macro_column=macro)
            self.add_top_macro_products_table(pdf, top_macro_df, macro_name, macro_column=macro)
            pdf.ln(10)

        nutriscore_image_path = self.get_image_path("nutriscore.png")
        pdf.add_page()
        self.add_section_title(pdf, "Nutri-Score Analysis")
        plot_nutriscore(self.df, filename=nutriscore_image_path)
        pdf.image(nutriscore_image_path, x=10, y=30, w=180)

        pdf_path = self.get_pdf_path("report.pdf")
        pdf.output(pdf_path)

        for filename in os.listdir("jpg"):
            if filename.startswith(str(self.unique_id)):
                os.remove(os.path.join("jpg", filename))

        print(f"Report generated: {pdf_path}")
        return pdf_path


@dataclass
class ProductEntry:
    code: str
    date: datetime
    quantity: int = 1


product_codes = [
    "20724696",
    "5449000214911",
    "8076800195057",
    "0062639358631",
    "8426904171042",
    "00980326",
    "5390003011260"
]


def generate_november_entries(product_codes):
    entries = []
    start_date = datetime(2024, 11, 1)
    end_date = datetime(2024, 11, 30)

    current_date = start_date
    while current_date <= end_date:
        for code in random.sample(product_codes, k=random.randint(1, len(product_codes))):
            quantity = random.randint(1, 5)
            entries.append(ProductEntry(code=code, date=current_date, quantity=quantity))
        current_date += timedelta(days=1)
    return entries

"""
product_entries = generate_november_entries(product_codes)

report_generator = ProductReportGenerator(product_entries,unique_id=uuid.uuid4(), month=11, year=2024)
pdf_path = report_generator.generate_pdf_report()
"""

