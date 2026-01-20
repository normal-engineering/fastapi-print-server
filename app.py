from fastapi import FastAPI, UploadFile, HTTPException, File, Form, Request
from fastapi.responses import JSONResponse, FileResponse

import cups 
import tempfile

from pydantic import TypeAdapter
from typing import Any, TypedDict
import subprocess
import os

from datetime import datetime

import uuid

from db.bucket import download_pdf_from_bucket

app = FastAPI()

# class PrintJob(BaseModel):
#     file: UploadFile = None
#     printer_name: str = "default_printer"
#     copies: int = 1

type_dict = {
    'batch' : '明細表',
    'packing' : '理貨單',
    'label' : '宅配貼紙'
}

class PrintJob(TypedDict):
    sub: str
    type: str
    date_delivery: datetime
    device_id: str
    printer_name: str

def print_file_with_cups(file_path: str, printer_name: str = None):
    """Sends a file to a CUPS printer."""
    try:
        conn = cups.Connection()
        printers = conn.getPrinters()

        if not printers:
            raise HTTPException(status_code=503, detail="No printers found in CUPS")

        # Use a default printer if none is specified, or validate the specified one
        if printer_name is None:
            printer_name = list(printers.keys())[0] # Use the first available printer
        elif printer_name not in printers:
            raise HTTPException(status_code=404, detail=f"Printer '{printer_name}' not found")

        # The printFile method handles various file formats (text, PDF, images, etc.)
        job_id = conn.printFile(printer_name, file_path, f"FastAPI Job: {os.path.basename(file_path)}", {})
        return {"message": "Print job submitted successfully", "job_id": job_id, "printer": printer_name}

    except cups.IPPError as e:
        raise HTTPException(status_code=500, detail=f"CUPS IPPError: {e.message}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {str(e)}")


@app.get("/")
async def test_connection():
    return {"message": "Print Server Online"}

@app.get("/print-list/")
async def check_printer_list():
    try: 
        response = subprocess.check_output("lpstat -p | awk '{print $2}'", shell=True) 
        return {"message": f"Printer List: {response}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving printer list: {str(e)}")

@app.post("/print-pdf/")
async def print_pdf(
    file: UploadFile = File(...), 
    printer: str = Form(None)  # Change this line - use Form() instead of default parameter
):
    # Validate file type
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    # Save to temp directory
    temp_filename = f"/tmp/{uuid.uuid4()}.pdf"
    with open(temp_filename, "wb") as f:
        f.write(await file.read())
    
    try:
        result = print_file_with_cups(temp_filename, printer)
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Print failed: {str(e)}")

    finally:
        # Cleanup
        if os.path.exists(temp_filename):
            os.remove(temp_filename)

@app.post("/print-bucket/")
async def print_pdf(request:Request):
    body = await request.body()
    print(body)
    ta_req = TypeAdapter(PrintJob)
    req = ta_req.validate_json(body)
    # Save to temp directory

    date = req['date_delivery'].strftime('%Y-%m')
    # date = '2026-01'
    type_converted = type_dict[req['type']]
    print(type_converted)
    temp_filename = f"{uuid.uuid4()}.pdf"
    bucket_filename = f"{date}/{type_converted}/{req['sub']}_{type_converted}.pdf"
    await download_pdf_from_bucket(s3_object_key=bucket_filename, local_file_path=temp_filename)
    
    try:
        result = print_file_with_cups(temp_filename, req['printer'])
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Print failed: {str(e)}")

    finally:
        # Cleanup
        if os.path.exists(temp_filename):
            os.remove(temp_filename)