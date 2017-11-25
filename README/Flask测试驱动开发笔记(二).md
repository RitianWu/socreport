# Part 1 — “千里之行，始于足下”

## 1.创建项目

这节我们会定义一个服务(APP，项目或者应用)，并搭建简单的项目结构。

---

创建一个新的项目，并安装**Flask**

```
$ mkdir socreport && cd socreport
$ mkdir project
$ python3.6 -m venv env
$ source env/bin/activate
(env)$ pip install flask==0.12.2
```

首先，在***project***文件夹中添加`__init__.py`文件，并配置我们的第一个路由：

```python
# project/__init__.py


from flask import Flask, jsonify

# instantiate the app
app = Flask(__name__)


@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })
```

然后，添加**[Flask-Script](https://flask-script.readthedocs.io/en/latest/)**，方便我们通过命令行来运行和管理应用程序:

```
(env)$ pip install flask-script==2.0.6
```

在***socreport***下添加`manage.py`文件:

```python
# manage.py


from flask_script import Manager

from project import app

manager = Manager(app)

if __name__ == '__main__':
    manager.run()
```

通过创建一个**Manager**实例来处理所有命令行指令，例如运行应用程序：

```
(env)$ python manage.py runserver
```

打开浏览器，浏览<http://localhost:5000/ping>可以看到如下内容:

```json
{
  "message": "pong!",
  "status": "success"
}
```

接下来，我们停止应用程序，并在***project***文件夹下添加配置文件`config.py`:

```python
# project/config.py


class BaseConfig:
    """Base configuration"""
    DEBUG = False
    TESTING = False


class DevelopmentConfig(BaseConfig):
    """Development configuration"""
    DEBUG = True


class TestingConfig(BaseConfig):
    """Testing configuration"""
    DEBUG = True
    TESTING = True


class ProductionConfig(BaseConfig):
    """Production configuration"""
    DEBUG = False
```

紧接着，更新`__init__.py`文件，将DevelopmentConfig添加到配置项中:

```python
# project/__init__.py


from flask import Flask, jsonify

# instantiate the app
app = Flask(__name__)

# set config
app.config.from_object('project.config.DevelopmentConfig')


@app.route('/ping', methods=['GET'])
def ping_pong():
    return jsonify({
        'status': 'success',
        'message': 'pong!'
    })
```

再次运行代码，应当可以看到这次项目启动开启了调试模式(**[debug mode](http://flask.pocoo.org/docs/0.12/quickstart/#debug-mode)**):

```
$ python manage.py runserver
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
 * Restarting with stat
 * Debugger is active!
 * Debugger PIN: 107-952-069
```

现在，项目调试运行期间，一旦代码发生了改变，应用程序就会进行重载。那最后，让我终止应用程序，并通过**deactivate**命令退出虚拟环境，在项目根目录下(***socreport***)添加项目依赖文件`requirements.txt`:

> 在虚拟环境中，可以使用**pip freeze**查看当前环境配置的所有依赖；
>
> 可以使用重定向命令，将所有依赖导入到依赖文件中；
>
> 也可以选择只添加主要依赖(其他依赖会在主要的依赖模块安装过程中下载安装)。

```
Flask==0.12.2
Flask-Script==2.0.6
```

最后，将项目提交到**Git**版本库进行版本控制，所有还要添加一个`.gitignore`文件在我们的项目根目录下:

```
__pycache__
env
```

初始化一个Git仓库，并提交我们的代码。