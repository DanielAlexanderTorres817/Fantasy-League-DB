from flask_sqlalchemy import SQLAlchemy
import random

# Initialize SQLAlchemy
db = SQLAlchemy()

# Example User Model
def generate_unique_id():
    """Generate a unique 8-digit numeric ID."""
    while True:
        new_id = random.randint(10000000, 99999999)
        if not User.query.filter_by(id=new_id).first():  # Check if it's unique
            return new_id

class User(db.Model):
    """Users Table"""
    __tablename__ = 'Users'
    id = db.Column(db.Numeric(8, 0), primary_key=True, default=generate_unique_id)
    name = db.Column(db.String(50))
    email = db.Column(db.String(50), nullable=False)
    username = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(64), nullable=False)  # Should be hashed/encrypted
    profile_settings = db.Column(db.Text)

    # Unique constraints
    __table_args__ = (
        db.UniqueConstraint('email', 'username'),
    )