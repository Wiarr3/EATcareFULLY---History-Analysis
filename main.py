import os
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from typing import List
import uuid
from apscheduler.schedulers.background import BackgroundScheduler
from pydantic import BaseModel

from report_generator import ProductReportGenerator

class ProductEntry(BaseModel):
    code: str
    date: datetime
    quantity: int = 1
class AnalyzeProductsRequest(BaseModel):
    products: List[ProductEntry]

app = FastAPI()

@app.get("/")
def read_root():
    return {"It works"}

@app.post("/start/")
async def analyze_products(products: AnalyzeProductsRequest):
    unique_id = uuid.uuid4()
    report_generator = ProductReportGenerator(products, month=11, year=2024, unique_id=unique_id)
    report_generator.generate_pdf_report()

    pdf_filename = f"{unique_id}_report.pdf"
    pdf_path = os.path.join("pdf", pdf_filename)

    if not os.path.exists(pdf_path):
        raise HTTPException(status_code=404, detail="PDF file not found")

    return FileResponse(pdf_path, media_type="application/pdf", filename=pdf_filename)

EXPIRATION_TIME = timedelta(minutes=10)


def delete_old_files():
    print("check files for delete")
    now = datetime.now()
    for filename in os.listdir("pdf"):
        file_path = os.path.join("pdf", filename)

        if os.path.isfile(file_path):
            file_modified_time = datetime.fromtimestamp(os.path.getmtime(file_path))
            if now - file_modified_time > EXPIRATION_TIME:
                try:
                    os.remove(file_path)
                    print(f"Deleted old file: {filename}")
                except Exception as e:
                    print(f"Error deleting file {filename}: {e}")


scheduler = BackgroundScheduler()
scheduler.add_job(delete_old_files, "interval", minutes=5)
scheduler.start()

