# Part1 — “Flask Blueprint(蓝图)”

测试已经到位，让我们通过添加蓝图来重构应用程序...

------

> 如果不太熟悉Flask蓝图，可以查看[官方文档](http://flask.pocoo.org/docs/0.12/blueprints/)介绍。简单概括一下，实质上，蓝图是自包含的组件，用于封装代码，模板和静态文件。

在 `project` 下新建一个 `api` 文件夹，添加 `__init__.py` ，并新增 `views.py`和 `models.py`。更新 `views.py` 文件:

```python
# project/api/views.py


from flask import Blueprint, jsonify

report_blueprint = Blueprint('report', __name__)


@report_blueprint.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })

```

这里，我们新建了一个 `Blueprint` 的实例，并将 `ping_pong` 函数绑定在这个实例上。

更新 `models.py`文件:

```python
# project/api/models.py


from project import db


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

```

更新 `project/__init__.py`:

```python
# project/__init__.py

import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# instantiate the db
db = SQLAlchemy()


def create_app():
    # instantiate the app
    app = Flask(__name__)

    # set config
    app_settings = os.getenv('APP_SETTINGS')
    app.config.from_object(app_settings)

    # set up extensions
    db.init_app(app)

    # register blueprints
    from project.api.views import report_blueprint
    app.register_blueprint(report_blueprint)

    return app

```

更新 `manage.py`:

```python
# manage.py

import unittest

from flask_script import Manager
from project import create_app, db

app = create_app()
manager = Manager(app)


@manager.command
def test():
    """Runs the tests without code coverage."""
    tests = unittest.TestLoader().discover('project/tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1


@manager.command
def recreate_db():
    """Recreates a database."""
    db.drop_all()
    db.create_all()
    db.session.commit()


if __name__ == '__main__':
    manager.run()

```

更新 `project/tests/base.py` 和 `project/tests/test_config.py`的引用:

```python
from project import create_app

app = create_app()

```

(记得在`base.py` 中引入 `db`)

更新完毕，测试一下!

```
$ docker-compose up -d
$ docker-compose run report-service python manage.py recreate_db
$ docker-compose run report-service python manage.py test

```