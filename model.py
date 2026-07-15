from datetime import datetime, timezone
from extensions import db
from flask_login import UserMixin

class User(UserMixin,db.Model): # turns this python class into a mapped Table managed by SQLAlchemy
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default = False)

    def to_dict(self):
        return{
            "id": self.id,
            "username": self.username,
            "is_admin": self.is_admin,
        }
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(200))
    content = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    owner = db.relationship("User", backref="notes")

    def to_dict(self):
        return{
            "id": self.id,
            "owner_id": self.owner_id, # in normal apps this wouldn't be coded because it returns the owner_id of the note
            "title": self.title,
            "content": self.content,
            "created_at": self.created_at.isoformat(),
        }
    