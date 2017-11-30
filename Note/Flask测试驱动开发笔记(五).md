# Part1 — “开始测试”

![](https://www.fiddlerscode.com/uploads/2/2/1/6/22168498/i-recommend-lets-play-tdd-570x320_1_orig.jpg)

开始我们的测试之旅...

------

在 `project` 中添加 `tests` 文件夹，然后在新的文件夹中创建以下文件:

```
$ touch __init__.py base.py test_config.py test_users.py

```

依次为各个文件添加代码内容...

`__init__.py`:

```python
# project/tests/__init__.py

```

`base.py`:

```python
# project/tests/base.py


from flask_testing import TestCase

from project import app, db


class BaseTestCase(TestCase):
    def create_app(self):
        app.config.from_object('project.config.TestingConfig')
        return app

    def setUp(self):
        db.create_all()
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

```

`test_config.py`:

```python
# project/tests/test_config.py


import unittest

from flask_testing import TestCase

from flask import current_app
from project import app


class TestDevelopmentConfig(TestCase):
    def create_app(self):
        app.config.from_object('project.config.DevelopmentConfig')
        return app

    def test_app_is_development(self):
        self.assertTrue(app.config['SECRET_KEY'] == 'my_precious')
        self.assertTrue(app.config['DEBUG'] is True)
        self.assertFalse(current_app is None)
        self.assertTrue(
            app.config['SQLALCHEMY_DATABASE_URI'] ==
            'postgres://postgres:postgres@report-db:5432/report_dev'
        )


class TestTestingConfig(TestCase):
    def create_app(self):
        app.config.from_object('project.config.TestingConfig')
        return app

    def test_app_is_testing(self):
        self.assertTrue(app.config['SECRET_KEY'] == 'my_precious')
        self.assertTrue(app.config['DEBUG'])
        self.assertTrue(app.config['TESTING'])
        self.assertFalse(app.config['PRESERVE_CONTEXT_ON_EXCEPTION'])
        self.assertTrue(
            app.config['SQLALCHEMY_DATABASE_URI'] ==
            'postgres://postgres:postgres@report-db:5432/report_test'
        )


class TestProductionConfig(TestCase):
    def create_app(self):
        app.config.from_object('project.config.ProductionConfig')
        return app

    def test_app_is_production(self):
        self.assertTrue(app.config['SECRET_KEY'] == 'my_precious')
        self.assertFalse(app.config['DEBUG'])
        self.assertFalse(app.config['TESTING'])


if __name__ == '__main__':
    unittest.main()

```

`test_report.py`:

```python
# project/tests/test_report.py


import json

from project.tests.base import BaseTestCase


class TestReportService(BaseTestCase):
    """Tests for the Report Service."""

    def test_report(self):
        """Ensure the /ping route behaves correctly."""
        response = self.client.get('/ping')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('pong!', data['message'])
        self.assertIn('success', data['status'])

```

将依赖 [Flask-Testing](https://pythonhosted.org/Flask-Testing/) 添加到 `requirements.txt` 文件中:

```
Flask-Testing==0.6.2

```

在 `mangage.py` 中添加新的命令，用于发现和运行测试代码:

```python
@manager.command
def test():
    """Runs the tests without code coverage."""
    tests = unittest.TestLoader().discover('project/tests', pattern='test*.py')
    result = unittest.TextTestRunner(verbosity=2).run(tests)
    if result.wasSuccessful():
        return 0
    return 1

```

不要忘了引入 `unittest`:

```python
import unittest

```

现在，我们需要重新构建镜像，这是因为项目依赖会在镜像构建时装载，而非运行时:

```
$ docker-compose up -d --build

```

各容器建立完成并启动运行，我们可以测试代码:

```
$ docker-compose run users-service python manage.py test

```

测试代码运行过程中将会看到错误信息:

```python
self.assertTrue(app.config['SECRET_KEY'] == 'my_precious')

```

依据错误信息，更新项目配置文件:

```python
class BaseConfig:
    """Base configuration"""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'my_precious'

```

再吃进行测试，完美通过!

```
Starting report-db ... done
test_app_is_development (test_config.TestDevelopmentConfig) ... ok
test_app_is_production (test_config.TestProductionConfig) ... ok
test_app_is_testing (test_config.TestTestingConfig) ... ok
test_report (test_report.TestReportService)
Ensure the /ping route behaves correctly. ... ok

----------------------------------------------------------------------
Ran 4 tests in 0.211s

OK

```