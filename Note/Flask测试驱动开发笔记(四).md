# Part 1 — “配置Postgres”

## 1.数据模型

![](https://deepstreamhub.com/open-source/integrations/db-postgres/postgres-deepstream.svg)

该部分将介绍如何配置Postgres数据库，并在另一个容器内运行，最终与 `reports-service`容器建立连接...

------

添加 *Flask-SQLAlchemy* 和 *psycopg2* 依赖到 `requirements.txt` 文件:

```
Flask-SQLAlchemy==2.3.2
psycopg2==2.7.3.2

```

更新 `config.py`:

```python
# project/config.py

import os


class BaseConfig:
    """Base configuration"""
    DEBUG = False
    TESTING = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False


class DevelopmentConfig(BaseConfig):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')


class TestingConfig(BaseConfig):
    """Testing configuration"""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_TEST_URL')


class ProductionConfig(BaseConfig):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

```

更新 `__init__.py` ，目的是创建新的SQLAlchemy实例并定义数据库模型:

```python
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


```

在 `project` 下添加 `db` 文件夹，并在新的 `db` 文件夹下添加`create.sql`文件:

```sql
CREATE DATABASE report_prod;
CREATE DATABASE report_dev;
CREATE DATABASE report_test;

```

同时，在相同的文件夹下添加 `Dockerfile` 文件:

```dockerfile
FROM postgres

# run create.sql on init
ADD create.sql /docker-entrypoint-initdb.d

```

这里，我们相当于扩充了官方Postgres镜像，主要是在容器中添加了一个SQl文件到 `docker-entrypoint-initdb.d`文件夹下，其目的是在初始化的时候运行该脚本，创建数据库。

更新 `docker-compose.yml`文件:

```dockerfile
version: '2.1'

services:

  report-db:
    container_name: report-db
    build: ./project/db
    ports:
      - 5435:5432 # expose ports - HOST:CONTAINER
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    healthcheck:
      test: exit 0

  report-service:
    container_name: report-service
    build: ./
    volumes:
      - '.:/usr/src/app'
    ports:
      - 5001:5000 # expose ports - HOST:CONTAINER
    environment:
      - APP_SETTINGS=project.config.DevelopmentConfig
      - DATABASE_URL=postgres://postgres:postgres@report-db:5432/report_dev
      - DATABASE_TEST_URL=postgres://postgres:postgres@report-db:5432/report_test
    depends_on:
      report-db:
        condition: service_healthy
    links:
      - report-db
```

一旦运行，环境变量首先会被添加，紧接着，如果容器成功启动退出代码0就会被发送。在宿主机器上，Postgres可以通过端口5435进行访问，对应容器中运行的数据库服务，其端口为5432.

我们来运行命令看看效果如何:

```
$ docker-compose up -d --build

```

修改文件 `manage.py`:

```python
# manage.py


from flask_script import Manager

from project import app, db

manager = Manager(app)


@manager.command
def recreate_db():
    """Recreates a database."""
    db.drop_all()
    db.create_all()
    db.session.commit()


if __name__ == '__main__':
    manager.run()

```

这里新增了一条指令，`recreate_db`，通过manager的配置我们可以很方便的从命令行来执行数据库重建操作:

```
$ docker-compose run report-service python manage.py recreate_db

```

Did this work? Let's hop into psql...

检验是否生效？通过psql我们来看一看...

```
$ docker exec -ti $(docker ps -aqf "name=report-db") psql -U postgres

# \c report_dev
You are now connected to database "report_dev" as user "postgres".

# \dt
         List of relations
 Schema |  Name  | Type  |  Owner
--------+--------+-------+----------
 public | report | table | postgres
(1 row)

# \q

```