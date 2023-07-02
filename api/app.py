import connexion
from flask_cors import CORS
import environment as env
from flask_sqlalchemy import SQLAlchemy


app_instance = connexion.App(__name__, specification_dir="./openAPI/")
app_instance.add_api("swagger.yml")

app = app_instance.app

CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = env.db_uri
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["PROPAGATE_EXCEPTIONS"] = True

db = SQLAlchemy()


@app.before_first_request
def create_tables():
    db.create_all()


if __name__ == "__main__":
    db.init_app(app)
    app.run(port=env.port, debug=True)


