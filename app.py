# app.py (Revised for Perplexity API with Animated Status Logic)

import os
import json
import base64
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv 
from PIL import Image
import io

# Use the 'requests' library directly since the Perplexity Python SDK
# is not always available or required for simple API calls.
import requests 

# --- LOAD ENVIRONMENT VARIABLES ---
load_dotenv()
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY")

app = Flask(__name__)

# --- API Configuration ---
PERPLEXITY_API_URL = "https://api.perplexity.ai/chat/completions"
# Use a model known to support multimodal (image) input.
# NOTE: This model is NOT free. Billing is required.
MODEL_NAME = "sonar-pro" 

# --- SYSTEM PROMPT (Optimized for Perplexity) ---
# We still force a JSON output to cleanly extract the required data fields.
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

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/detect', methods=['POST'])
def detect_currency():
    if not PERPLEXITY_API_KEY:
        return jsonify({"error": "Perplexity API Key not configured in .env.", "speech_text": "Error: API not configured."}), 500

    if 'image' not in request.files:
        return jsonify({"error": "No image file provided.", "speech_text": "Error: No image received."}), 400

    image_file = request.files['image']

    try:
        # 1. Image Preprocessing: PIL to Base64
        img = Image.open(io.BytesIO(image_file.read()))
        # Perplexity requires the image as a Base64 Data URI within the content payload
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG")
        img_str = base64.b64encode(buffer.getvalue()).decode()
        data_uri = f"data:image/jpeg;base64,{img_str}"

        # 2. Perplexity API Payload
        payload = {
            "model": MODEL_NAME,
            "messages": [
                {
                    "role": "system",
                    "content": SYSTEM_PROMPT
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Analyze this Indian banknote image and return the JSON structure exactly as requested in the system prompt."
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": data_uri}
                        }
                    ]
                }
            ]
        }
        
        headers = {
            "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        # 3. API Call
        response = requests.post(PERPLEXITY_API_URL, headers=headers, json=payload)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 4. Process Response
        response_data = response.json()
        raw_text = response_data['choices'][0]['message']['content'].strip()

        # The model is forced to return JSON, we attempt to parse it
        try:
            # Clean up potential markdown formatting (```json...)
            json_text = raw_text.replace('```json', '').replace('```', '').strip()
            result_json = json.loads(json_text)

            # Ensure 'full_validation' is boolean, as PPLX might return strings
            result_json['full_validation'] = str(result_json.get('full_validation', 'false')).lower() == 'true'

            return jsonify(result_json), 200
        except json.JSONDecodeError:
            return jsonify({
                "error": "Perplexity returned unparsable JSON.",
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
        return jsonify({"error": f"Server processing error: {e}", "speech_text": "Internal error."}), 500

if __name__ == '__main__':
    print("Starting Flask server for Perplexity API processing...")
    app.run(host='0.0.0.0', port=5000, debug=True)
