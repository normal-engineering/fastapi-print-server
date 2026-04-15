from fastapi import FastAPI, UploadFile, HTTPException, File, Form, Request
from fastapi.responses import JSONResponse, FileResponse

import cups 
import tempfile

from pydantic import TypeAdapter
from typing import Any, TypedDict
from pydantic import BaseModel
from typing_extensions import NotRequired
import subprocess
import os

from datetime import datetime

import uuid
from renders.reportlab.reportlab_label import create_shipping_label_code39

from db.bucket import download_pdf_from_bucket

app = FastAPI()

class PrintJob(BaseModel):
    file: UploadFile = None
    printer_name: str = "default_printer"
    copies: int = 1

type_dict = {
    'batch' : '明細表',
    'packing' : '理貨單',
    'label' : '宅配貼紙'
}

printer_dict = {
    "router" : "FUJIFILM_Apeos_C5570_66_23_85",
    "1" : "Brother_HL_L2460DW",
    "2" : "Brother_HL_L2460DW_94ddf88e25fb",
    "3" : "Brother_HL_L2460DW_94ddf88e24e7",
    "4" : "Brother_HL_L2460DW_94ddf88e25e9",
    "5" : "Brother_HL_L2460DW_94ddf88e35fa"
}

phone_id = { 
    "red-1":"98BA3739-B0B8-4BE3-956F-CDA1240CA5A7",
    "purple-2": "17C41332-312D-4C65-AB6D-DF0061DF2709",
    "green-3": "C57DFDB5-2130-4C30-9A60-44D871D2D49B",
    "black-4": "9C8DB7C8-19A9-46FE-8B1A-D0A67F795AE2", 
    "white-5": "3443422A-FD19-412C-AC18-0B1ADD40292B",
    }


class PrintJob(TypedDict):
    sub: str 
    type: str
    date_delivery: datetime
    device_id: str
    printer: str

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

# @app.get("/test-print")
# async def test_reportlab():
#     sample_data = {
#         'obtnumber': '907572734046',  # Code39 compatible value
#         'date_shipping': '2026-02-01',
#         'date_delivery': '2026-02-03',
#         'time_delivery_start': '14:00',
#         'time_delivery_end': '16:00',
#         'postnumber': '83-820-02-B',  # Code39 compatible value
#         'sub': 'O25003669002',
#         'customer': '林安琪(黃鼎喻/王奕雯)',
#         'transport':'黑貓宅急便',
#         'thermo':'常溫',
#         'comment':'請安排2/2-2/3出貨，出貨後約1-3 個工作日到貨 婚期2026/1/31 出貨前，請先拍照給玟妤確認，謝謝',
#         'customer_no': '0032368',
#         'customer_id': '428609240200',
#         'address': '116台北市文山區羅斯福路五段273號2樓',
#         'recipient': '林月霜',
#         'mobile': '0933039896',
#         'fulfillment.address': '235450新北市中和區中正路1215號2樓',
#         'company': '巧櫻有限公司',
#         'fulfillment.phone':'0233652252'
#     }

#     create_shipping_label_code39('shipping_label_code39_TEST.pdf', sample_data)
#     return {"message": "Test ReportLab Print"}

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


class PrintBucketRequest(TypedDict):
    sub: NotRequired[str] = None
    date_range: NotRequired[str] = None
    document: NotRequired[str] = None
    device: NotRequired[str] = None

@app.post("/bucket/")
async def print_pdf_from_bucket(request:Request):
    body = await request.body()
    print(body)
    ta_req = TypeAdapter(PrintBucketRequest)
    req = ta_req.validate_json(body)
    print(req)
    return req
    # Save to temp directory
    # date = req['date_range'][0].strftime('%Y-%m')
    # date = req['date_range'][0]
    # type_converted = type_dict[req['type']]
    # print(type_converted)
    # temp_filename = f"{uuid.uuid4()}.pdf"
    # bucket_filename = f"{date}/{type_converted}/{req['sub']}_{type_converted}.pdf"
    # await download_pdf_from_bucket(s3_object_key=bucket_filename, local_file_path=temp_filename)

    # try:
    #     with open(temp_filename, 'rb') as file:
    #         file.read()

    #         if req['device'] == 'MAIN':
    #             result = print_file_with_cups(file, os.getenv('MAIN'))
    #         else:
    #             result = print_file_with_cups(file, printer_dict[req['device']])
            
    #         return result

    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"Print failed: {str(e)}")

    # finally:
    #     # Cleanup
    #     if os.path.exists(temp_filename):
    #         os.remove(temp_filename)