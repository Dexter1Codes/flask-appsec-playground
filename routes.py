from flask import Blueprint, request, abort
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from extensions import db ,login_manager
from model import User, Note

bp = Blueprint("main", __name__)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

def get_owned_note_or_error(note_id):
    note = db.session.get(Note, note_id)
    if note is None:
        abort(404)
    if note.owner_id != current_user.id:
        abort(404)                       # 403 if clients are trusted.
    return note

@bp.route("/")
def index():
    return {"status": "ok"}

@bp.route("/register", methods=["POST"])
def register():
    data =  request.get_json()
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return {"error": "Incomplete Credentials"}, 400

    if User.query.filter_by(username=username).first():
        return {"error": "Username is already taken"}, 409
    
    user = User(
        username = username,
        password_hash = generate_password_hash(password),
    )
    db.session.add(user)
    db.session.commit()

    return {"message": "User generated successfully", "id": user.id}, 201


@bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username).first()

    if user is None or not check_password_hash(user.password_hash, password):
        return {"error": "Invalid Credentials"}, 401
    
    login_user(user)
    return {"message": "Logged In successfully", "id": user.id}, 200

@bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    return {"message": "Logged Out successfully"}, 200

@bp.route("/notes", methods=["POST"])
@login_required
def create_note():
    data = request.get_json()
    title = data.get("title")
    content = data.get("content")

    if not title:
        return {"error": "Title is a required field"}, 400
    
    note = Note(
        owner_id = current_user.id,
        title = title,
        content = content,
    )

    db.session.add(note)
    db.session.commit()
    return note.to_dict(), 201

@bp.route("/admin/users", methods=["GET"])
@login_required
def list_all_users():
    if not current_user.is_admin:
        abort(403)
    users = User.query.all()
    return {"users": [user.to_dict() for user in users]}, 200

@bp.route("/notes/mine", methods=["GET"])
@login_required
def my_notes():
    notes = Note.query.filter_by(owner_id=current_user.id).all()
    return {"notes": [note.to_dict() for note in notes]}, 200

@bp.route("/notes/<int:note_id>", methods=["GET"])
@login_required
def get_note(note_id):
    note = get_owned_note_or_error(note_id)
    return note.to_dict(), 200    

@bp.route("/notes/<int:note_id>", methods=["PATCH"])
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


@bp.route("/notes/<int:note_id>", methods=["DELETE"])
@login_required
def delete_note(note_id):
    note = get_owned_note_or_error(note_id)
    db.session.delete(note)
    db.session.commit()
    return {"message": "deleted"}, 200
