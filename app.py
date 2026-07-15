from flask import Flask, request, abort
from extensions import db, login_manager
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required,    current_user
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///notes.db"
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

db.init_app(app)
login_manager.init_app(app)

from model import User, Note

with app.app_context():
    db.create_all()

def get_owned_note_or_error(note_id):
    note = db.session.get(Note, note_id)
    if note is None:
        abort(404)
    if note.owner_id != current_user.id:
        abort(404)                       # 403 if clients are trusted.
    return note

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

@app.route("/notes", methods=["POST"])
@login_required
def create_note():
    data = request.get_json()
    title = data.get("title")
    content = data.get("content")

    if not title:
        return {"error": "Title Required"}, 400
    
    note  = Note(
        owner_id = current_user.id,
        title = title,
        content = content,
    )

    db.session.add(note)
    db.session.commit()
    return note.to_dict(), 201

@app.route("/admin/users", methods=["GET"])
@login_required
def list_all_users():
    users = User.query.all()
    return {"users": [user.to_dict() for user in users]}, 200

@app.route("/notes/mine", methods=["GET"])
@login_required
def my_notes():
    notes = Note.query.filter_by(owner_id=current_user.id).all()
    return {"notes": [note.to_dict() for note in notes]}, 200


@app.route("/notes/<int:note_id>", methods=["GET"])
@login_required
def get_note(note_id):
    note = get_owned_note_or_error(note_id)
    return note.to_dict(), 200    

@app.route("/notes/<int:note_id>", methods=["PATCH"])
@login_required
def update_note(note_id):
    note = get_owned_note_or_error(note_id)
    data = request.get_json()
    if "title" in data:
        note.title = data["title"]
    if "content" in data:
        note.content = data["content"]
    db.session.commit()
    return note.to_dict(), 200


@app.route("/notes/<int:note_id>", methods=["DELETE"])
@login_required
def delete_note(note_id):
    note = get_owned_note_or_error(note_id)
    db.session.delete(note)
    db.session.commit()
    return {"message": "deleted"}, 200


if __name__ == "__main__":
    debug_mode = os.environ.get("FLASK_DEBUG") == "1"
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=debug_mode)