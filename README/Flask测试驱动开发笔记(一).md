# Part 1 — “简单介绍”

## 1.概述

这是整个学习笔记的第一部分，这里，我们将介绍如何使用*Docker*快速搭建一个可复用(Reproducible，可复制或再现的)的开发环境；进而，使用*Python*，*Postgre*，以及*Flask* Web框架创建*RESTful API*；最后，应用在本地环境完美运行后，我们将学习如何将应用部署到类似*Amazon EC2*这样的云主机上。

> 考虑使用测试驱动开发(TDD，Test Derive Development)的方式，最初，我们将首先完成一些测试方法。

![test](https://testdriven.io/assets/img/flask-tdd-logo.png)

该系列学习笔记将使用的一些工具和技术：

**Part 1**

1. Python v3.6.2
2. Flask v0.12.2
3. Flask-Script v2.0.6
4. Flask-SQLAlchemy v2.3.2
5. Flask-Testing v0.6.2
6. psycopg2 v2.7.1
7. Gunicorn v19.7.1
8. Nginx v1.13.0
9. Docker v17.09.0-ce
10. Docker Compose v1.16.1
11. Docker Machine v0.12.2

**Part 2**

1. Coverage.py v4.4.1
2. Node v8.1.2
3. NPM v5.0.3
4. Create React App v1.3.0
5. Axios v0.16.2
6. Flask-CORS v3.0.2

**Part 3**

1. Flask-Migrate v2.1.2
2. Flask-Bcrypt v0.7.1
3. PyJWT v1.4.2
4. react-router-dom v4.1.1
5. React Bootstrap v0.31.0
6. React Router Bootstrap v0.24.2

**Part 4**

1. TestCafe v0.16.1
2. node-randomstring v1.1.5
3. Swagger UI v3.0.8

**Part 6**

1. Flask v0.12.2
2. Flask-Cors v3.0.3
3. Flask-Script v2.0.6
4. Flask-Testing v0.6.2
5. Gunicorn v19.7.1
6. Coverage.py v4.4.1
7. Requests v2.18.4
8. Flask-SQLAlchemy v2.3.2
9. Flask-Migrate v2.1.2
10. psycopg2 v2.7.1
11. React-Ace v5.2.1

开始学习之前，你应该对以下主题有足够的了解。

| Topic          | Resource                                 |
| -------------- | ---------------------------------------- |
| Docker         | [Get started with Docker](https://docs.docker.com/engine/getstarted/) |
| Docker Compose | [Get started with Docker Compose](https://docs.docker.com/compose/gettingstarted/) |
| Docker Machine | [Docker Machine Overview](https://docs.docker.com/machine/overview/) |
| Flask          | [Welcome to Flask](http://flask.pocoo.org/) |

## 2.目标

第一部分结束时，你应当具备以下几个方面的能力...

1. 使用Flask开发RESTful API
2. 对于测试驱动开发(TDD)有所认识
3. 使用Docker，Docker Compose，以及Docker Machine完成本地开发环境配置和实例运行
4. 使用*卷(Volums)*将代码*挂载(Mount)*在*容器(Container)*中
5. 在一个Docker容器内运行单元和集成测试
6. 不同容器内运行的服务间实现通信会话
7. Docker容器内使用Python并运行Flask
8. 在云主机上安装Flask，Ngnix，以及Gunicorn

## 3.应用说明

以报表管理为例，将要实现的后端接口如下...

| Endpoint     | HTTP Method | CRUD Method | Result            |
| ------------ | ----------- | ----------- | ----------------- |
| /reports     | GET         | READ        | get all reports   |
| /reports/:id | GET         | READ        | get single report |
| /reports     | POST        | CREATE      | add a report      |

> `/reports` POST endpoint将在笔记第三部分进行介绍。

总体上，该项目将运行在三个容器上—Flask ，Postgres，和Nginx。完成第一部分的学习，你将实现以上接口功能和系统部署。后面的部分，我们将添加用户认证和其他的一些服务。

## 4.代码

[获取代码](https://github.com/realpython/flask-microservices-users/releases/tag/part1)