from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
import torch

# Load model
model = DistilBertForSequenceClassification.from_pretrained("./rodchecker_saved_model")
tokenizer = DistilBertTokenizerFast.from_pretrained("./rodchecker_saved_model")

def predict_email(email_text):
    inputs = tokenizer(email_text, return_tensors="pt", truncation=True)
    with torch.no_grad():
        logits = model(**inputs).logits
    prediction = torch.argmax(logits, dim=-1).item()
    if prediction == 1:
        return "Phishing / Spam Email 🚨"
    else:
        return "Legit Email ✅"

# Example
email = "Did you finish work last week?"
print(predict_email(email))