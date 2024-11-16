from openfoodfacts import API, APIVersion, Country, Environment, Flavor
import uuid
import pandas as pd
import re
import time
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_product_with_retry(code, max_retries=5, delay=2):
    for attempt in range(max_retries):
        api = API(
            user_agent=f"EatcareFully${attempt}",
            username=None,
            password=None,
            country=Country.world,
            flavor=Flavor.off,
            version=APIVersion.v2,
            environment=Environment.org,
        )
        try:
            product = api.product.get(code)
            return product
        except Exception as e:
            print(f"Error while fetching: {code}: {e}. Attempt: {attempt + 1} of {max_retries}.")

        time.sleep(delay)

    print("Failed to fetch product")
    return None

def extract_macronutrients(nutrients):
    return {
        "energy_kcal": nutrients.get("energy-kcal_100g", 0),
        "fat": nutrients.get("fat_100g", 0),
        "saturated_fat": nutrients.get("saturated-fat_100g", 0),
        "carbohydrates": nutrients.get("carbohydrates_100g", 0),
        "sugars": nutrients.get("sugars_100g", 0),
        "proteins": nutrients.get("proteins_100g", 0),
        "salt": nutrients.get("salt_100g", 0),
    }


def extract_quantity_info(quantity_str):
    match = re.match(r"(\d+\.?\d*)\s*(\w+)", quantity_str)
    if match:
        value = float(match.group(1))
        unit = match.group(2).lower()

        if unit == "kg":
            value *= 1000
        elif unit == "l":
            value *= 1000

        return value, "g"
    return None, None

def scale_macronutrients(macro, weight):

    scale_factor = weight / 100
    return {k: v * scale_factor for k, v in macro.items()}


def process_data(product_entries):
    records = []

    for entry in product_entries.products:
        code = entry.code
        date = entry.date
        quantity = entry.quantity

        product = get_product_with_retry(code)
        if product is None:
            print(f"Product with code: {code} was not found.")
            continue
        name = product.get('product_name', "unknown")
        nutriments = product.get('nutriments', {})
        macro_per_100g = extract_macronutrients(nutriments)

        nutriscore = product.get("nutriscore_grade", "N/A")
        fruits_vegetables_nuts_estimate = nutriments.get("fruits-vegetables-nuts-estimate-from-ingredients_100g", 0)
        categories = product.get("categories", "N/A")

        quantity_str = product.get("quantity", "N/A")
        weight_value, weight_unit = extract_quantity_info(quantity_str)

        if weight_value:
            macro_scaled = scale_macronutrients(macro_per_100g, weight_value)
        else:
            macro_scaled = macro_per_100g

        for _ in range(quantity):
            record = {
                "id": uuid.uuid4(),
                "code": code,
                "name": name,
                "date": date,
                "weight_value": weight_value,
                "weight_unit": weight_unit,
                "energy_kcal_100g": macro_per_100g["energy_kcal"],
                "fat_100g": macro_per_100g["fat"],
                "saturated_fat_100g": macro_per_100g["saturated_fat"],
                "carbohydrates_100g": macro_per_100g["carbohydrates"],
                "sugars_100g": macro_per_100g["sugars"],
                "proteins_100g": macro_per_100g["proteins"],
                "salt_100g": macro_per_100g["salt"],
                "energy_kcal_total": macro_scaled["energy_kcal"],
                "fat_total": macro_scaled["fat"],
                "saturated_fat_total": macro_scaled["saturated_fat"],
                "carbohydrates_total": macro_scaled["carbohydrates"],
                "sugars_total": macro_scaled["sugars"],
                "proteins_total": macro_scaled["proteins"],
                "salt_total": macro_scaled["salt"],
                "nutriscore": nutriscore,
                "fruits_vegetables_nuts_estimate": fruits_vegetables_nuts_estimate,
                "categories": categories,
            }
            records.append(record)

    return pd.DataFrame(records)
