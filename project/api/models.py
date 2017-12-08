# project/api/models.py


from project import db


class Report(db.Model):
    __tablename__ = "report"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(256), nullable=False)
    url = db.Column(db.String(512), nullable=False, unique=True)
    deleted = db.Column(db.Boolean, server_default='0')
    create_time = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)
    update_time = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(),
                            onupdate=db.func.current_timestamp(), index=True)

    def __init__(self, name, url):
        self.name = name
        self.url = url
