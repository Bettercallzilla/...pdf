import os
import uuid
from fastapi import FastAPI, UploadFile, File, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pdf2image import convert_from_path
import pytesseract
import requests

UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ocr/file")
async def ocr_from_file(file: UploadFile = File(...)):
    filename = f"{uuid.uuid4().hex}.pdf"
    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    try:
        images = convert_from_path(file_path)
        text = "\n".join([pytesseract.image_to_string(img) for img in images])
        return {"text": text}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/ocr/url")
async def ocr_from_url(request: Request):
    data = await request.json()
    url = data.get("url")
    if not url:
        return JSONResponse(status_code=400, content={"error": "No URL provided."})

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        filename = f"{uuid.uuid4().hex}.pdf"
        file_path = os.path.join(UPLOAD_DIR, filename)
        with open(file_path, "wb") as f:
            f.write(response.content)

        images = convert_from_path(file_path)
        text = "\n".join([pytesseract.image_to_string(img) for img in images])
        return {"text": text}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
