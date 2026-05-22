from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect

db       = SQLAlchemy()
login_manager = LoginManager()
mail     = Mail()
migrate  = Migrate()
bcrypt   = Bcrypt()
csrf     = CSRFProtect()

login_manager.login_view         = 'auth.login'
login_manager.login_message      = 'Please log in.'
login_manager.login_message_category = 'danger'


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    import os
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    csrf.init_app(app)

    from .routes.static_pages import static_pages_bp
    from .routes.auth         import auth_bp
    from .routes.users        import users_bp
    from .routes.rounds       import rounds_bp

    app.register_blueprint(static_pages_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(rounds_bp)

    return app
