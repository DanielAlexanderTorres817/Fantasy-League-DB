from flask import Flask
from views import views
# from flask_sqlalchemy import SQLAlchemy
from models import db

app = Flask(__name__)
app.secret_key = "super secret key"

app.register_blueprint(views, url_prefix = "/")

#DATABASE CODE HERE
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"  # SQLite database file
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # Disable unnecessary overhead


db.init_app(app)

with app.app_context():
    # db.drop_all() # testing purposes
    db.create_all()
    print("success!")

if __name__ == "__main__":
    app.run(debug=True, port = 8000)