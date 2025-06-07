import os
import uuid
import requests
from flask import Flask, request, jsonify
from pdf2image import convert_from_path
import pytesseract

UPLOAD_FOLDER = './uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/ocr-pdf', methods=['POST'])
def ocr_pdf():
    file = request.files.get('file')
    url = request.json.get('url') if request.is_json else None

    if not file and not url:
        return jsonify({"error": "No PDF file or URL provided"}), 400

    try:
        if file:
            filename = f"{uuid.uuid4().hex}.pdf"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
        else:
            response = requests.get(url, timeout=10)
            if response.status_code != 200 or 'application/pdf' not in response.headers.get('Content-Type', ''):
                return jsonify({"error": "Invalid or inaccessible PDF URL"}), 400
            filename = f"{uuid.uuid4().hex}.pdf"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            with open(filepath, 'wb') as f:
                f.write(response.content)

        images = convert_from_path(filepath)
        extracted_text = "\n".join(pytesseract.image_to_string(img) for img in images)
        return jsonify({"text": extracted_text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5055)
