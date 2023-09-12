import connexion
from flask_cors import CORS
import environment as env
from database.db import db

def create_app():
    app_instance = connexion.App(__name__, specification_dir="./openAPI/")
    app_instance.add_api("swagger.yml")

    app = app_instance.app

    CORS(app, vary_header=True, origins=env.frontend_URI, supports_credentials=True)

    app.config["SQLALCHEMY_DATABASE_URI"] = env.db_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.secret_key = env.flask_secret_key

    db.init_app(app)

    @app.before_first_request
    def create_tables():
        db.create_all()

    return app
app = create_app()

if __name__ == "__main__":
    app.run(port=env.port, debug=True, host="0.0.0.0")


