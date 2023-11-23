import connexion
from flask_cors import CORS
import environment as env
from database.db import db
import uvicorn
from asgiref.wsgi import WsgiToAsgi
from starlette.middleware.cors import CORSMiddleware
from connexion.middleware import MiddlewarePosition
from environment import logging
import contextlib




def create_app():
    app_instance = connexion.FlaskApp(__name__, specification_dir="./openAPI/")
    app_instance.add_middleware(
    CORSMiddleware,
    position=MiddlewarePosition.BEFORE_ROUTING,
    allow_origins=env.frontend_URI,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
    app_instance.add_api("swagger.yml")

    app = app_instance.app

    app.config["SQLALCHEMY_DATABASE_URI"] = env.db_uri
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["PROPAGATE_EXCEPTIONS"] = True
    app.secret_key = env.flask_secret_key
    db.init_app(app)
    

    return app_instance
app = create_app()

@app.app.before_request
def before_request():
    if not env.are_all_tables_created:
        with app.app.app_context():
            db.create_all()
            db.session.commit()
            logging.info("✅  Tables created")
            logging.info(db.metadata.tables.keys())
            env.are_all_tables_created = True

    


if __name__ == "__main__":
   uvicorn.run("app:app", host="0.0.0.0", port=env.port, reload=True)
   


