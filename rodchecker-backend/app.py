from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
import torch
import re
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
from user_model import db, User, bcrypt

# === Load model + tokenizer ===
model = DistilBertForSequenceClassification.from_pretrained("../rodchecker_saved_model")
tokenizer = DistilBertTokenizerFast.from_pretrained("../rodchecker_saved_model")

# === Setup Flask ===
app = Flask(__name__)
CORS(app)

# === URL detector ===
def has_url(text):
    return bool(re.search(r"http[s]?://", text))

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://roduser:rodpass123@localhost/rodchecker"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


jwt = JWTManager(app)
db.init_app(app)
bcrypt.init_app(app)

with app.app_context():
    db.create_all()

@app.route("/predict", methods=["POST"])
@jwt_required()
def predict():
    username = get_jwt_identity() 
    print(f"Prediction made by: {username}") 
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

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if User.query.filter_by(username=data["username"]).first():
        return jsonify({"msg": "Username already exists"}), 400

    new_user = User(username=data["username"])
    new_user.set_password(data["password"])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({"msg": "User created"}), 201

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    user = User.query.filter_by(username=data["username"]).first()
    if user and user.check_password(data["password"]):
        access_token = create_access_token(identity=user.username)
        return jsonify(access_token=access_token)
    return jsonify({"msg": "Invalid credentials"}), 401


if __name__ == "__main__":
    app.run(debug=True)
