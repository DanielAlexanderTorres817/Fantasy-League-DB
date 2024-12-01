from flask import Flask
from flask_migrate import Migrate
from views import views
# from flask_sqlalchemy import SQLAlchemy
from models import db

import pymysql
pymysql.install_as_MySQLdb()

app = Flask(__name__)
app.secret_key = "super secret key"

app.register_blueprint(views, url_prefix = "/")

#DATABASE CODE HERE
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"  # SQLite database file
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/database_project' # test xxamp
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False  # Disable unnecessary overhead

db.init_app(app)

migrate = Migrate(app, db)

with app.app_context():
    # db.drop_all() # testing purposes
    db.create_all()
    print("success!")

if __name__ == "__main__":
    app.run(debug=True, port = 8000)