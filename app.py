# app.py (Full Version for Perplexity API + Mobile-Friendly Frontend)

import os
import json
import base64
from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from PIL import Image
import io
import requests

# --- Load Environment Variables ---
load_dotenv()
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")

app = Flask(__name__)
CORS(app)  # Allow cross-origin requests for mobile/web frontend

# --- Perplexity API Configuration ---
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"
MODEL_NAME = "sonar-pro"

SYSTEM_PROMPT = """
You are a highly accurate currency note identifier. You are given an image of an Indian banknote (₹10, ₹20, ₹50, ₹100, ₹200, ₹500). The note can be front or back.

Your task is to:
1. Identify the side (front/back) and denomination (10, 20, 50, 100, 200, 500).
2. Set 'full_validation' to TRUE only if the side and denomination are clearly verifiable (e.g., Gandhi + RBI for front, Monument + Denomination for back).
3. Generate a 'speech_text' output that clearly states the denomination.

Output ONLY a single, strictly valid JSON object. DO NOT include any introductory or explanatory text.
{
  "side": "front" | "back",
  "denomination": 10 | 20 | 50 | 100 | 200 | 500 | "null",
  "full_validation": true | false,
  "speech_text": "It is a <denomination> Rupees note." | "Note not clear, please show the note fully."
}
If detection fails, set 'denomination' to "null" and provide the appropriate 'speech_text'.
"""

# --- Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/detect', methods=['POST'])
def detect_currency():
    if not PERPLEXITY_API_KEY:
        return jsonify({"error": "Perplexity API Key not configured in .env.", 
                        "speech_text": "Error: API key not configured."}), 500

    if 'image' not in request.files:
        return jsonify({"error": "No image provided.", 
                        "speech_text": "Error: No image received."}), 400

    image_file = request.files['image']

    try:
        # --- Convert image to Base64 ---
        img = Image.open(io.BytesIO(image_file.read()))
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG")
        img_str = base64.b64encode(buffer.getvalue()).decode()
        data_uri = f"data:image/jpeg;base64,{img_str}"

        # --- Prepare Perplexity API Payload ---
        payload = {
            "model": MODEL_NAME,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": [
                    {"type": "text", "text": "Analyze this Indian banknote image and return the JSON exactly as requested in the system prompt."},
                    {"type": "image_url", "image_url": {"url": data_uri}}
                ]}
            ]
        }

        headers = {
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        # --- Call Perplexity API ---
        response = requests.post(PERPLEXITY_API_URL, headers=headers, json=payload)
        response.raise_for_status()

        # --- Parse Perplexity Response ---
        raw_text = response.json()['choices'][0]['message']['content'].strip()
        try:
            json_text = raw_text.replace('```json','').replace('```','').strip()
            result_json = json.loads(json_text)
            # Ensure full_validation is boolean
            result_json['full_validation'] = str(result_json.get('full_validation','false')).lower() == 'true'
            return jsonify(result_json), 200
        except json.JSONDecodeError:
            return jsonify({
                "error": "Perplexity returned invalid JSON.",
                "raw_response": raw_text,
                "speech_text": "Analysis failed. Server returned unstructured response."
            }), 500

    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code
        if status_code == 401:
            speech_err = "API key error. Check your Perplexity key."
        elif status_code == 429:
            speech_err = "Rate limit exceeded. Too many requests."
        else:
            speech_err = f"Perplexity API Error: {status_code}"
        return jsonify({"error": str(e), "speech_text": speech_err}), status_code

    except Exception as e:
        return jsonify({"error": f"Server processing error: {e}", "speech_text": "Internal server error."}), 500


# --- Main ---
if __name__ == '__main__':
    print("Starting Flask server for Perplexity API...")
    app.run(host='0.0.0.0', port=5000, debug=True)
