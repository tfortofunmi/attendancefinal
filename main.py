from flask import Flask, render_template, redirect, url_for, request, session
from forms import LoginForm
from werkzeug.security import generate_password_hash
import os
from admin.routes import admin_bp
from user.routes import user_bp

from flask_login import LoginManager
from models import (
    User, db, create_tables,
    create_super_admin, create_semester,
    create_levels
)
from config import config

login_manager = LoginManager()
login_manager.login_view = 'admin.login'
login_manager.login_message = 'Please log in as an admin to access this page.'

def create_app():
    app = Flask(__name__)
    # app.config['SECRET_KEY'] = 'your-secret'
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///yourdb.db'
    app.config.from_object(config)
    db.init_app(app)
    login_manager.init_app(app)
    # # Call create_tables after init_app
    create_tables(app)
    # create super admin
    verify = input("Is this the first time you are running the script (Y/N)? ")
    if verify.lower() == "y":
        create_super_admin(app)
        create_semester(app)
        create_levels(app)
    
    app.register_blueprint(admin_bp)
    app.register_blueprint(user_bp)
    return app

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Ensure instance folder exists
os.makedirs('instance', exist_ok=True)

app = create_app()

@app.route('/')
def index():
    return render_template("/common_view/index.html" )


if __name__=="__main__":
    app.run(debug=True)