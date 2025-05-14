from flask import Flask, request, jsonify
from flask_cors import CORS
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
import torch
import re
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_sqlalchemy import SQLAlchemy
from user_model import db, User, bcrypt, PredictionLog
from sqlalchemy import func

# === Load model + tokenizer ===
model = DistilBertForSequenceClassification.from_pretrained("../rodchecker_saved_model")
tokenizer = DistilBertTokenizerFast.from_pretrained("../rodchecker_saved_model")

# === Setup Flask ===
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql://roduser:rodpass123@localhost/rodchecker"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = "123"

# ✅ Correct CORS setup
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}}, supports_credentials=True)



jwt = JWTManager(app)
db.init_app(app)
bcrypt.init_app(app)

with app.app_context():
    db.create_all()

@app.route("/predict", methods=["POST"])
@jwt_required()
def predict():
    username = get_jwt_identity()
    data = request.get_json()
    email_text = data["email"]

    # URL flag + classification
    url_flag = 1 if "http" in email_text else 0
    formatted_text = f"URL_FLAG_{url_flag} {email_text}"

    inputs = tokenizer(formatted_text, return_tensors="pt", truncation=True)
    with torch.no_grad():
        logits = model(**inputs).logits
    prediction = torch.argmax(logits, dim=-1).item()

    result = "Phishing 🚨" if prediction == 1 else "Legit ✅"

    new_log = PredictionLog(
        username=username,
        email_text=email_text,
        prediction_result=result
    )
    db.session.add(new_log)
    db.session.commit()

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


@app.route("/dashboard", methods=["GET"])
@jwt_required()
def dashboard():
    username = get_jwt_identity()
    print("Dashboard requested by:", username)

    total = db.session.query(func.count(PredictionLog.id)).filter_by(username=username).scalar()
    legit = db.session.query(func.count(PredictionLog.id)).filter_by(username=username, prediction_result="Legit ✅").scalar()
    phishing = db.session.query(func.count(PredictionLog.id)).filter_by(username=username, prediction_result="Phishing 🚨").scalar()

    return jsonify({
        "total": total,
        "legit": legit,
        "phishing": phishing
    })

@app.after_request
def apply_cors_headers(response):
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    return response

if __name__ == "__main__":
    app.run(debug=True)
