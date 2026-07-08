from flask import Flask, request
from extensions import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
import os

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///notes.db"
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

db.init_app(app)
login_manager.init_app(app)

from model import User, Note

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route("/")
def index():
    return {"status": "ok"}

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return {"error": "Username is a required field"}, 400
    
    if User.query.filter_by(username = username).first():
        return{"error": "Username already taken"}, 409
    
    user = User(
        username = username,
        password_hash = generate_password_hash(password),
    )
    db.session.add(user)
    db.session.commit()

    return {"message": "registered", "id": user.id}, 201

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()

    if user is None or not check_password_hash(user.password_hash, password):
        return {"error": "Invalid Credentials"}, 401
    
    login_user(user)
    return{"message": "logged In", "ID": user.id}, 200

@app.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return {"message": "logged Out Successfully"}, 200

if __name__ == "__main__":
    app.run(debug=True)