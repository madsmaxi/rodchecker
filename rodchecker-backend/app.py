from flask import Flask, request, jsonify
from transformers import DistilBertForSequenceClassification, DistilBertTokenizerFast
from flask_cors import CORS
import torch

#Loading model... 
model = DistilBertForSequenceClassification.from_pretrained("../rodchecker_saved_model")
tokenizer = DistilBertTokenizerFast.from_pretrained("../rodchecker_saved_model")


app = Flask(__name__)
CORS(app)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    email_text = data['email']

    inputs = tokenizer(email_text, return_tensors="pt", truncation=True)
    with torch.no_grad():
        logits = model(**inputs).logits
    prediction = torch.argmax(logits, dim=-1).item()

    result = "Phishing 🚨" if prediction == 1 else "Legit ✅"
    return jsonify({'prediction': result})

if __name__ == '__main__':
    app.run(debug=True)

