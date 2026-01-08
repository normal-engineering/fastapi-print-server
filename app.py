from fastapi import FastAPI, UploadFile, HTTPException, File, Form
from fastapi.responses import JSONResponse, FileResponse

import cups 
import tempfile

from pydantic import BaseModel
from typing import Any
import subprocess
import os
import requests

import uuid

app = FastAPI()

class PrintJob(BaseModel):
    file: UploadFile = None
    printer_name: str = "default_printer"
    copies: int = 1

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
    return {"message": "Hello World"}

@app.get("/print-list/")
async def check_printer_list():
    try: 
        response = subprocess.check_output("lpstat -p | awk '{print $2}'", shell=True) 
        return {"message": f"Printer List: {response}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving printer list: {str(e)}")

@app.post("/print-pdf/")
async def print_pdf(file: UploadFile = File(...), printer: Form(None)):
    # Validate file type
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    # Save to temp directory
    temp_filename = f"/tmp/{uuid.uuid4()}.pdf"
    # Write uploaded.pdf → /tmp/uuid.pdf
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