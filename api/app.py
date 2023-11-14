import connexion
from flask_cors import CORS
import environment as env
from database.db import db
import uvicorn
from asgiref.wsgi import WsgiToAsgi


def create_app():
    app_instance = connexion.FlaskApp(__name__, specification_dir="./openAPI/")
    app_instance.add_api("swagger.yml")

    app = app_instance.app

    CORS(app, vary_header=True, origins=env.frontend_URI, supports_credentials=True)

    app.config["SQLALCHEMY_DATABASE_URI"] = env.db_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.secret_key = env.flask_secret_key

    db.init_app(app)

    with app.app_context():
        db.create_all()

    return app_instance
app = create_app()

if __name__ == "__main__":
   app.run(port=env.port,  host="0.0.0.0",  )
  # uvicorn.run("app:app", host="0.0.0.0", port=env.port, reload=True)


