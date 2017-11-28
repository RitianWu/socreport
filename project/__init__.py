# project/__init__.py

import os

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy

# instantiate the app
app = Flask(__name__)

# set config
app_settings = os.getenv('APP_SETTINGS')
app.config.from_object(app_settings)

# instantiate the db
db = SQLAlchemy(app)


# model
class Report(db.Model):
    __tablename__ = "report"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(256), nullable=False)
    url = db.Column(db.String(512), nullable=False)
    deleted = db.Column(db.Boolean, server_default='0')
    create_time = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)
    update_time = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(),
                            onupdate=db.func.current_timestamp(), index=True)

    def __init__(self, name, url):
        self.name = name
        self.url = url


# routes
@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })
