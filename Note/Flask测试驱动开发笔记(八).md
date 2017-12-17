#Part1 — “部署”

完成了测试和路由程序，接下来开始部署程序!

> 由于没有云主机，这里没有对AWS的部署过程进行实测。如果是独立服务器部署，以下内容也具有一定的参考意义。

------

如果需要的话，依据 [官网](http://docs.aws.amazon.com/AWSEC2/latest/UserGuide/get-set-up-for-amazon-ec2.html) 说明完成 AWS 的注册，并创建 IAM 用户(如果需要的话)，最终确保在你的个人主目录下添加证书(*~/.aws/credentials*)文件。然后创建一个新的docker宿主引擎：

```
$ docker-machine create --driver amazonec2 aws

```

> 针对AWS上的Docker配置，可以参考 [Amazon Web Services (AWS) EC2 example](https://docs.docker.com/machine/examples/aws/)。

完成后，将其设置为活动主机，并将Docker客户端指向它：

```
$ docker-machine env aws
$ eval $(docker-machine env aws)

```

运行以下命令查看当前运行的机器：

```
$ docker-machine ls

```

创建一个新的docker-compose文件，命名为 *docker-compose-prod.yml*，文件内容参考其他docker-compose文件，最主要的是要排除掉 `volumes`相关内容。

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

> 还记得volumes的作用吗？

分离容器，创建数据库，种子数据，并运行测试：

```
$ docker-compose -f docker-compose-prod.yml up -d --build
$ docker-compose -f docker-compose-prod.yml run report-service python manage.py recreate_db
$ docker-compose -f docker-compose-prod.yml run report-service python manage.py seed_db
$ docker-compose -f docker-compose-prod.yml run report-service python manage.py test

```

将端口5001添加到[安全组](http://stackoverflow.com/questions/26338301/ec2-how-to-add-port-8080-in-security-group)中。

获取IP地址，并在浏览器中测试。

#### Config配置项

线上部署我们应该使用生产环境配置项，因此需要修改我们的环境变量。首先来看一下我们现在使用的配置项:

```
$ docker-compose -f docker-compose-prod.yml run report-service env

```

可以看到，环境变量`APP_SETTINGS`被定义为`project.config.DevelopmentConfig`。

修改`docker-compose-prod.yml`中的环境变量：

```
environment:
    - APP_SETTINGS=project.config.ProductionConfig
    - DATABASE_URL=postgres://postgres:postgres@report-db:5432/report_prod
    - DATABASE_TEST_URL=postgres://postgres:postgres@report-db:5432/report_test

```

更新后运行测试:

```
$ docker-compose -f docker-compose-prod.yml up -d

```

重新创建数据库，并添加种子数据：

```
$ docker-compose -f docker-compose-prod.yml run report-service python manage.py recreate_db
$ docker-compose -f docker-compose-prod.yml run report-service python manage.py seed_db

```

#### 使用Gunicorn

使用Gunicorn之前，首先添加项目依赖到文件`requirements.txt`中:

```
gunicorn==19.7.1

```

然后对应更新配置文件，主要是在report-service中添加`command`:

```
command: gunicorn -b 0.0.0.0:5000 manage:app

```

该命令会覆盖`services/users/Dockerfile`中的`CMD`的命令( `python manage.py runserver -h 0.0.0.0`)。

再次更新运行：

```
$ docker-compose -f docker-compose-prod.yml up -d --build

```

> The `--build` flag is necessary since we need to install the new dependency
>
> 需要使用`—build`的参数标识，是因为我们更新了依赖，需要重新构建镜像。

#### 使用Nginx

接下来，WEB应用中的反向代理不用多说。我们在项目根路径下来创建一个新的文件夹—“nginx”，然后在文件夹中添加一个`Dockerfile`：

```dockerfile
FROM nginx:1.13.0

RUN rm /etc/nginx/conf.d/default.conf
ADD /flask.conf /etc/nginx/conf.d

```

同样，在“nginx”文件夹下需要添加配置文件`flask.conf`：

```nginx
server {

    listen 80;

    location / {
        proxy_pass http://report-service:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

}

```

同样在生产环境配置文件中添加`nginx`服务：

```dockerfile
nginx:
  container_name: nginx
  build: ./nginx/
  restart: always
  ports:
    - 80:80
  depends_on:
    report-service:
      condition: service_started
  links:
    - report-service

```

与此同时，删除report服务中对外暴露的端口(删除`ports`项)，只对其他容器暴露5000端口：

```
expose:
  - '5000' # expose port - CONTAINER

```

然后重修构建镜像，运行容器：

```
$ docker-compose -f docker-compose-prod.yml up -d --build nginx

```

同样的，我们来更新一下本地的环境。

首先，添加nginx到配置文件`docker-compose.yml`中：

```
nginx:
  container_name: nginx
  build: ./nginx/
  restart: always
  ports:
    - 80:80
  depends_on:
    report-service:
      condition: service_started
  links:
    - report-service

```

然后，我们需要激活本地主机引擎。我们可以先检查下当前处于激活状态的主机：

```
$ docker-machine active
aws

```

修改激活的主机为开发机器`dev`：

```
$ eval "$(docker-machine env dev)"

```

然后运行nginx容器：

```
$ docker-compose up -d --build nginx

```

最后本地浏览器测试，此时访问地址将不需要端口号。
