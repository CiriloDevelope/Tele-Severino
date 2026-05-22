from flask import Flask
from .config import Config


def create_app():
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static"
    )

    app.config.from_object(Config)

    from .routes.auth_routes import auth_bp
    from .routes.main_routes import main_bp
    from .routes.specialist_routes import specialist_bp
    from .routes.call_routes import call_bp
    from .routes.payment_routes import payment_bp
    from .routes.review_routes import review_bp
    from .routes.brand_routes import brand_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(specialist_bp)
    app.register_blueprint(call_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(review_bp)
    app.register_blueprint(brand_bp)

    return app
