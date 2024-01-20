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
from flask_apscheduler import APScheduler
from monitoring.sentry import sentry_configuration
from flask_migrate import Migrate



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
    Migrate(app, db)

    
    db.init_app(app)
    sentry_configuration() #optional
    

    return app_instance
app = create_app()
scheduler = APScheduler()
scheduler.init_app(app.app)
scheduler.start()

flask_application = app.app

@scheduler.task('interval', id='clean_email_verification_token_from_db', hours=12, misfire_grace_time=900)
def clean_email_verification_token_from_db():
    with app.app.app_context():
        logging.info("🧹  Cleaning email verification tokens from database")
        from database.model import EmailVerificationToken
        from datetime import datetime
        tokens = db.session.query(EmailVerificationToken).all()
        for token in tokens:
            if float(token.expiration) < datetime.now().timestamp():
                db.session.delete(token)
                db.session.commit()
                logging.info(f"❌  Deleted token for user {token.user_id} at {datetime.now()}")


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
   


