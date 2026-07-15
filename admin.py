from app import app, db
from model import User

with app.app_context():
    user = User.query.filter_by(username="admin_user").first()
    if user is None:
        print("User is not Registered, Register him/her first.")
    else:
        user.is_admin=True
        db.session.commit() # It is needed because the mutated attribute is changed only in memory, not in written, this `.commit()` makes sure it is flushed and written to the DB. 
        print(f"{user.username} is now admin: {user.is_admin}")