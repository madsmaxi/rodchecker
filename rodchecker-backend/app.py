from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
import torch
import re

# === Load model + tokenizer ===
model = DistilBertForSequenceClassification.from_pretrained("../rodchecker_saved_model")
tokenizer = DistilBertTokenizerFast.from_pretrained("../rodchecker_saved_model")

# === Setup Flask ===
app = Flask(__name__)
CORS(app)

# === URL detector ===
def has_url(text):
    return bool(re.search(r"http[s]?://", text))

@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    email_text = data["email"]

    # Inject URL flag
    url_flag = 1 if has_url(email_text) else 0
    formatted_text = f"URL_FLAG_{url_flag} {email_text}"

    # Tokenize + predict
    inputs = tokenizer(formatted_text, return_tensors="pt", truncation=True)
    with torch.no_grad():
        logits = model(**inputs).logits
    prediction = torch.argmax(logits, dim=-1).item()

    result = "Phishing 🚨" if prediction == 1 else "Legit ✅"
    return jsonify({"prediction": result})

if __name__ == "__main__":
    app.run(debug=True)
