# Part 1 — “配置Docker”

## 1.容器化(Containerize)

![](https://sdtimes.com/wp-content/uploads/2015/01/0120.sdt-docker-infographic.png)

简单来说，就是我们要用Docker将Flask应用进行集装箱式打包...

------

首先需要确定你的系统里已经安装过Docker，Docker Comose，以及Docker Machine:

```
$ docker -v
Docker version 17.09.0-ce, build afdb6d4
$ docker-compose -v
docker-compose version 1.16.1, build 6d1ac21
$ docker-machine -v
docker-machine version 0.12.2, build 9371605

```

接下来，我们需要借助 **[Docker Machine](https://docs.docker.com/machine/)** **[创建](https://docs.docker.com/machine/reference/create/)** 一个Docker引擎主机，并将Docker客户端指向创建的主机:

```
$ docker-machine create -d virtualbox dev
$ eval "$(docker-machine env dev)"

```

> 通过**[这里](https://stackoverflow.com/questions/40038572/eval-docker-machine-env-default/40040077#40040077)**可以了解更多以上命令详情.

在项目根目录下添加 `Dockerfile` 文件:

```dockerfile
FROM python:3.6.2

# set working directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# add requirements (to leverage Docker cache)
ADD requirements.txt /usr/src/app/requirements.txt

# install requirements
RUN pip install -r requirements.txt

# add app
ADD . /usr/src/app

# run server
CMD python manage.py runserver -h 0.0.0.0

```

然后添加 `docker-compose.yml` 文件到根目录下:

```yaml
version: '2.1'

services:

  reports-service:
    container_name: reports-service
    build: .
    volumes:
      - '.:/usr/src/app'
    ports:
      - 5001:5000 # expose ports - HOST:CONTAINER
      
```

依赖Dockerfile配置文件将会创建一个名为 `reports-service`的容器。

 参数`volume`是将代码挂载在容器中。这样做主要是出于开发环境的考虑，目的是当应用程序代码发生变化时，对应更新容器。如果不这样做，就需要每次更新代码后，重建一次镜像。

应当注意使用的[Docker Compose 文件版本](https://docs.docker.com/compose/compose-file/) - `2.1`。注意该版本号跟你安装的Docker Compose的版本没有直接关系—它仅仅标识你所使用的文件格式。

构建镜像:

```
$ docker-compose build

```

首次构建镜像可能需要一段时间，但由于Docker在第一次构建镜像过程中进行了缓存，随后的构建过程会快很多。构建完成，立即启动容器:

```
$ docker-compose up -d

```

>  `-d` 标识用于后台运行该容器。

查看启动的容器IP地址:

```
$ docker-machine ip dev

```

浏览器打开连接地址[http://YOUR-IP:5001/ping](http://your-ip:5001/ping)(这里的IP是宿主机器的IP)，将看到和之前相同的JSON返回数据。然后，在 `docker-compose.yml` 中添加dev环境变量:

```
version: '2.1'

services:

  reports-service:
    container_name: reports-service
    build: .
    volumes:
      - '.:/usr/src/app'
    ports:
      - 5001:5000 # expose ports - HOST:CONTAINER
    environment:
      - APP_SETTINGS=project.config.DevelopmentConfig

```

紧接着在更新代码文件 `project/__init__.py`，引入环境变量:

```
# project/__init__.py

import os

from flask import Flask, jsonify

# instantiate the app
app = Flask(__name__)

# set config
app_settings = os.getenv('APP_SETTINGS')
app.config.from_object(app_settings)


@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })

```

更新容器:

```
$ docker-compose up -d

```

好吧，我们来测试一下，比如说在 `__init__.py` 文件中添加一条输出语句，来看一看我们的配置项:

```python
print(app.config)

```

查看日志的命令如下:

```
$ docker-compose logs -f reports-service

```

可以看到的配置项内容如下:

```
<Config {
  'DEBUG': True, 'TESTING': False, 'PROPAGATE_EXCEPTIONS': None,
  'PRESERVE_CONTEXT_ON_EXCEPTION': None, 'SECRET_KEY': None,
  'PERMANENT_SESSION_LIFETIME': datetime.timedelta(31), 'USE_X_SENDFILE':
  False, 'LOGGER_NAME': 'project', 'LOGGER_HANDLER_POLICY': 'always',
  'SERVER_NAME': None, 'APPLICATION_ROOT': None, 'SESSION_COOKIE_NAME':
  'session', 'SESSION_COOKIE_DOMAIN': None, 'SESSION_COOKIE_PATH': None,
  'SESSION_COOKIE_HTTPONLY': True, 'SESSION_COOKIE_SECURE': False,
  'SESSION_REFRESH_EACH_REQUEST': True, 'MAX_CONTENT_LENGTH': None,
  'SEND_FILE_MAX_AGE_DEFAULT': datetime.timedelta(0, 43200),
  'TRAP_BAD_REQUEST_ERRORS': False, 'TRAP_HTTP_EXCEPTIONS': False,
  'EXPLAIN_TEMPLATE_LOADING': False, 'PREFERRED_URL_SCHEME': 'http',
  'JSON_AS_ASCII': True, 'JSON_SORT_KEYS': True,
  'JSONIFY_PRETTYPRINT_REGULAR': True, 'JSONIFY_MIMETYPE':
  'application/json', 'TEMPLATES_AUTO_RELOAD': None}
>

```

记得最后删除 `print` 语句哦。