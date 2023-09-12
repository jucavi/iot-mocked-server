from flask import Flask, g
from server.routes import mocked
import sqlite3
from datetime import timedelta
from flask_cors import CORS
import json

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "SECRET_KEY"
    app.config["TIMEZONE"] = "Europe/Madrid"
    app.config['JSON_SORT_KEYS'] = False
    app.config['JSON_AS_ASCII'] = False
    app.config.from_file("config.json", load=json.load)
    app.config['PERMANENT_SESSION_LIFETIME'] =  timedelta(minutes=10)
    app.register_blueprint(mocked, url_prefix="/iot/")
    return app

app = create_app()
CORS(app)

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

if __name__ == "__main__":
    app.run(debug=app.config.get('DEBUG'), port=app.config.get('PORT'))