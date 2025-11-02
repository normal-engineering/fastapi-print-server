from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import subprocess
import os


app = FastAPI()

class PrintJob(BaseModel):
    file_path: str
    printer_name: str = "default_printer"
    copies: int = 1

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/print-list/")
async def handle_print_webhook():
    try: 
        response = subprocess.check_output("lpstat -p | awk '{print $2}'", shell=True) 
        return {"message": f"Printer List: {response}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting print job: {str(e)}")

@app.post("/print-webhook/")
async def handle_print_webhook(job: PrintJob):
    # Validate file existence (optional, but good practice)
    if not os.path.exists(job.file_path):
        raise HTTPException(status_code=404, detail=f"File not found: {job.file_path}")

    # Integrate with a printing library or system command
    try:
        # Example using a system command (Windows: print, Linux: lp)
        # This would need to be adapted based on your OS and printer setup
        if os.name == 'nt':  # Windows
            command = f'print /d:"{job.printer_name}" "{job.file_path}"'
        else:  # Linux/macOS
            command = ['/usr/bin/lp', '-d', job.printer_name, job.file_path]
        try:
            subprocess.run(command, check=True)
            return {"message": "Print job submitted successfully"}
        except subprocess.CalledProcessError as e:
            raise HTTPException(status_code=500, detail=f"Print command failed: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error submitting print job: {str(e)}")