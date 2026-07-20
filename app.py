from flask import Flask
from extensions import db, login_manager
from werkzeug.security import generate_password_hash
import os
from dotenv import load_dotenv
from model import User, Note
from routes import bp

load_dotenv()
def  create_app(config=None):
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///notes.db"
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
    if config:
        app.config.update(config)
    
    db.init_app(app)
    login_manager.init_app(app)

    app.register_blueprint(bp)

    with app.app_context():
        db.create_all()
        seed_admin()

    return app



def seed_admin():
    admin_username = os.environ.get("ADMIN_USERNAME")
    admin_password = os.environ.get("ADMIN_PASSWORD")

    if not admin_password or not admin_username:
        return
    existing_admin = User.query.filter_by(is_admin = True).first()
    if existing_admin:
        return
    
    admin = User(
        username = admin_username,
        password_hash = generate_password_hash(admin_password),
        is_admin = True,
    )

    db.session.add(admin)
    db.session.commit()

if __name__ == "__main__":
    app = create_app()
    debug_mode = os.environ.get("FLASK_DEBUG") == "1"
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug = debug_mode)