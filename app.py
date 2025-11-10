from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import JSONResponse

import cups 
import tempfile

from pydantic import BaseModel
from typing import Any
import subprocess
import os

app = FastAPI()

class PrintJob(BaseModel):
    file: UploadFile = None
    printer_name: str = "default_printer"
    copies: int = 1

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

# @app.post("/print-webhook/")
# async def handle_print_webhook(job: PrintJob | None = None):

#     if job.file is None:
#         raise HTTPException(status_code=400, detail="No file uploaded")

#     if not job.file.filename.lower().endswith(".pdf"):
#         raise HTTPException(status_code=400, detail="Only PDF files are supported")

#     # Save the uploaded PDF to a temp file
#     with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
#         tmp.write(await job.copyfile.read())
#         tmp_path = tmp.name
        
#     # Integrate with a printing library or system command
#     try:
#         # Connect to CUPS
#         conn = cups.Connection()
    

#         # Check if the printer exists
#         printers = conn.getPrinters()
#         if job.printer_name not in printers:
#             raise HTTPException(status_code=404, detail=f"Printer '{job.printer_name}' not found")

#         # Example using a system command (Windows: print, Linux: lp)
#         # This would need to be adapted based on your OS and printer setup
#     #     if os.name == 'nt':  # Windows
#     #         command = f'print /d:"{job.printer_name}" "{job.file_path}"'
#     #     else:  # Linux/macOS
#     #         command = ['/usr/bin/lp', '-d', job.printer_name, job.file_path]
#     #     try:
#     #         subprocess.run(command, check=True)
#     #         return {"message": "Print job submitted successfully"}
#     #     except subprocess.CalledProcessError as e:
#     #         raise HTTPException(status_code=500, detail=f"Print command failed: {e}")
#     # except Exception as e:
#     #     raise HTTPException(status_code=500, detail=f"Error submitting print job: {str(e)}")
    
#         job_id = conn.printFile(PrintJob.printer_name, tmp_path, job.file.filename, {})

#         return JSONResponse({
#             "status": "success",
#             "message": f"Print job {job_id} sent to printer '{job.printer_name}'."
#         })

#     except cups.IPPError as e:
#         raise HTTPException(status_code=500, detail=f"CUPS error: {e}")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Error: {e}")
#     finally:
#         # Clean up the temporary file
#         if os.path.exists(tmp_path):
#             os.remove(tmp_path)

@app.post("/print")
async def print_pdf(file: UploadFile, printer_name):
    """
    Upload a PDF file and send it to the local CUPS printer.
    """
    if file is None:
        raise HTTPException(status_code=400, detail="No file uploaded")

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    # Save the uploaded PDF to a temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        # Connect to CUPS
        conn = cups.Connection()

        # Check if the printer exists
        printers = conn.getPrinters()
        if printer_name not in printers:
            raise HTTPException(status_code=404, detail=f"Printer '{printer_name}' not found")

        # Send the job to the printer
        job_id = conn.printFile(printer_name, tmp_path, file.filename, {})

        return JSONResponse({
            "status": "success",
            "message": f"Print job {job_id} sent to printer '{printer_name}'."
        })

    except cups.IPPError as e:
        raise HTTPException(status_code=500, detail=f"CUPS error: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {e}")
    finally:
        # Clean up the temporary file
        if os.path.exists(tmp_path):
            os.remove(tmp_path)