# Part1 — “RESTful 路由”

![](https://tutorialedge.net/uploads/rest-api.png)

---

接下来，让我们按照RESTful最佳实践和TDD构建三个新的路由接口：

| 路由地址         | HTTP 方法 | 增删改查方法 | 结果描述       |
| ------------ | ------- | ------ | ---------- |
| /reports     | GET     | 查询     | 获取所有report |
| /reports/:id | GET     | 查询     | 获取单个report |
| /reports     | POST    | 添加     | 添加一个report |

对于每一个路由的实现，我们将遵循以下循环过程：

1. 写测试
2. 运行测试，测试失败(**红**)
3. 编写程序代码直到测试通过 (**绿**)
4. **重构代码** (如果需要的话)

首先来实现我们的添加方法(POST)...

#### POST

在 *project/tests/test_report.py* 的 `TestReportService()`类中添加测试方法:

```python
def test_add_report(self):
    """Ensure a new report can be added to the database."""
    with self.client:
        response = self.client.post(
            '/reports',
            data=json.dumps(dict(
                name='测试Report添加',
                url='暂无',
            )),
            content_type='application/json',
        )
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 201)
        self.assertIn('success', data['status'])
        self.assertIn('Report add success', data['message'])
        self.assertIn('report_id', data['data'])

```

运行测试，可以看到测试失败的结果：

```
$ docker-compose run users-service python manage.py test

```

然后在 *project/api/views.py* 中添加路由处理程序：

```python
@report_blueprint.route('/reports', methods=['POST'])
def add_report():
    post_data = request.get_json()
    name = post_data.get('name')
    url = post_data.get('url')
    db.session.add(Report(name=name, url=url))
    db.session.commit()
    response_object = {
                'status': 'success',
                'message': 'Report add success',
                'data': {
                    'report_id': report_object.id
                }
            }
    return jsonify(response_object), 201

```

更新引入模块：

```python
from flask import Blueprint, jsonify, request

from project.api.models import Report
from project import db

```

再次运行测试程序，测试通过：

```
Ran 5 tests in 0.201s

OK

```

针对一些错误和异常的处理，例如：

1. 未设置Payload；
2. Payload是不规范的，例如，JSON对象为空或者包含错误的Keys；
3. 添加的数据已经在数据库中存在；

针对以上示例添加测试：

```python
def test_add_report_invalid_json(self):
    """Ensure error is thrown if the JSON object is empty."""
    with self.client:
        response = self.client.post(
            '/reports',
            data=json.dumps(dict()),
            content_type='application/json',
        )
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 400)
        self.assertIn('fail', data['status'])
        self.assertIn('Invalid payload', data['message'])

def test_add_report_invalid_json_keys(self):
    """Ensure error is thrown if the JSON object does not have a url key."""
    with self.client:
        response = self.client.post(
            '/reports',
            data=json.dumps(dict(
                name='测试Report添加',
            )),
            content_type='application/json',
        )
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 400)
        self.assertIn('fail', data['status'])
        self.assertIn('Invalid payload', data['message'])

def test_add_report_duplicate_report(self):
    """Ensure error is thrown if the report already exists."""
    with self.client:
        self.client.post(
            '/reports',
            data=json.dumps(dict(
                name='测试Report添加',
                url='http://wiosky.com/test.jpg'
            )),
            content_type='application/json',
        )
        response = self.client.post(
            '/reports',
            data=json.dumps(dict(
                name='测试Report添加',
                url='http://wiosky.com/test.jpg',
            )),
            content_type='application/json',
        )
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 400)
        self.assertIn('fail', data['status'])
        self.assertIn('Report already exists', data['message'])

```

很显然此时测试未通过，紧接着更新我们的路由处理方法：

```python
@report_blueprint.route('/reports', methods=['POST'])
def add_report():
    post_data = request.get_json()
    if not post_data:
        response_object = {
            'status': 'fail',
            'message': 'Invalid payload'
        }
        return jsonify(response_object), 400
    name = post_data.get('name')
    url = post_data.get('url')
    try:
        report = Report.query.filter(Report.url == url).first()
        if not report:
            report_object = Report(name=name, url=url)
            db.session.add(report_object)
            db.session.commit()
            response_object = {
                'status': 'success',
                'message': 'Report add success',
                'data': {
                    'report_id': report_object.id
                }
            }
            return jsonify(response_object), 201
        else:
            response_object = {
                'status': 'fail',
                'message': 'Report already exists'
            }
            return jsonify(response_object), 400
    except exc.IntegrityError as e:
        db.session.rollback()
        response_object = {
            'status': 'fail',
            'message': 'Invalid payload'
        }
        return jsonify(response_object), 400
        
```

引入sqlalchemy异常：

```python
from sqlalchemy import exc

```

确保此刻测试通过，我们开始下一个路由方法的实现过程...

#### GET 单个Report

首先，测试显性：

```python
def test_single_report(self):
    """Ensure get single report behaves correctly."""
    report = Report(name='测试Report添加', url='http://wiosky.com/test.jpg')
    db.session.add(report_object)
    db.session.commit()
    with self.client:
        response = self.client.get('/reports/{report_id}'.format(report_id=report_object.id))
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', data['status'])
        self.assertIn('Query success', data['message'])
        self.assertIn('测试Report添加', data['data']['name'])
        self.assertIn('http://wiosky.com/test.jpg', data['data']['url'])
        self.assertTrue('create_time' in data['data'])

```

添加引用：

```python
from project import db
from project.api.models import Report

```

此刻测试依然无效，我们来添加路由视图方法：

```python
@report_blueprint.route('/reports/<report_id>', methods=['GET'])
def get_single_report(report_id):
    """Get single report details"""
    report = Report.query.filter_by(id=report_id).first()
    response_object = {
        'status': 'success',
        'message': 'Query success',
        'data': {
            'name': report_object.name,
            'url': report_object.url,
            'create_time': report_object.create_time
        }
    }
    return jsonify(response_object), 200

```

正常情况下，测试通过。针对异常情况，添加测试方法，异常情况例如：

1. 未指定id
2. id对应的数据不存在

测试方法：

```python
def test_single_report_no_id(self):
    """Ensure error is thrown if an id is not provided."""
    with self.client:
        response = self.client.get('/reports/blah')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 404)
        self.assertIn('fail', data['status'])
        self.assertIn('Report does not exist', data['message'])

def test_single_report_incorrect_id(self):
    """Ensure error is thrown if the id does not exist."""
    with self.client:
        response = self.client.get('/reports/999')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 404)
        self.assertIn('fail', data['status'])
        self.assertIn('Report does not exist', data['message'])

```

更新视图函数：

```python
@report_blueprint.route('/reports/<report_id>', methods=['GET'])
def get_single_report(report_id):
    """Get single report details"""
    response_object = {
        'status': 'fail',
        'message': 'Report does not exist'
    }
    try:
        report_object = Report.query.filter(Report.id == int(report_id)).first()
        if not report_object:
            return jsonify(response_object), 404
        else:
            response_object = {
                'status': 'success',
                'message': 'Query success',
                'data': {
                    'name': report_object.name,
                    'url': report_object.url,
                    'create_time': report_object.create_time
                }
            }
            return jsonify(response_object), 200
    except ValueError:
        return jsonify(response_object), 404

```

#### GET 所有Report

依旧如此，测试先行。但是，首先我们需要再数据库里添加一些数据，因此为了方便处理，在 *project/tests/test_users.py* 的顶部(`TestReportService()` 类上方)添加一个公共方法。

```python
def add_report(name, url):
    report_object = Report(name=name, url=url)
    db.session.add(report_object)
    db.session.commit()
    return report_object

```

借助该方法可以重构 *test_single_user()* 测试方法：

```python
def test_single_report(self):
    """Ensure get single report behaves correctly."""
    report_object = add_report('测试Report添加', 'http://wiosky.com/test.jpg')
    with self.client:
        response = self.client.get('/reports/{report_id}'.format(report_id=report_object.id))
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', data['status'])
        self.assertIn('Query success', data['message'])
        self.assertIn('测试Report添加', data['data']['name'])
        self.assertIn('http://wiosky.com/test.jpg', data['data']['url'])
        self.assertTrue('create_time' in data['data'])z

```

添加新的测试方法：

```python
def test_all_reports(self):
    """Ensure get all reports behaves correctly."""
    add_report('测试1', 'http://wiosky.com/test1.jpg')
    add_report('测试2', 'http://wiosky.com/test2.jpg')
    with self.client:
        response = self.client.get('/reports')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('success', data['status'])
        self.assertEqual(len(data['data']['reports']), 2)
        self.assertTrue('create_time' in data['data']['reports'][0])
        self.assertTrue('create_time' in data['data']['reports'][1])
        self.assertIn('测试1', data['data']['reports'][0]['name'])
        self.assertIn(
            'http://wiosky.com/test1.jpg', data['data']['reports'][0]['url'])
        self.assertIn('测试2', data['data']['reports'][1]['name'])
        self.assertIn(
            'http://wiosky.com/test2.jpg', data['data']['reports'][1]['url'])
```

再次，测试失败，添加视图方法：

```python
@report_blueprint.route('/reports', methods=['GET'])
def get_all_reports():
    """Get all reports"""
    reports = Report.query.all()
    reports_list = []
    for report in reports:
        report_object = {
            'id': report.id,
            'name': report.name,
            'url': report.url,
            'create_time': report.create_time
        }
        reports_list.append(report_object)
    response_object = {
        'status': 'success',
        'message': 'Query success',
        'data': {
            'reports': reports_list
        }
    }
    return jsonify(response_object), 200
```

测试通过了吗?

继续之前，让我们通过浏览器查看一下接口返回-[http://YOUR-IP:5001/reports](http://your-ip:5001/reports)。

```json
{
  "data": {
    "reports": [ ]
  },
  "status": "success"，
  "message": "Query success",
}

```

在 *manage.py* 中构建一条新的命令，方便用一些初始数据填充数据库：

```python
@manager.command
def seed_db():
    """Seeds the database."""
    db.session.add(Report(name='测试1', url='http://wiosky.com/test1.jpg'))
    db.session.add(Report(name='测试2', url='http://wiosky.com/test2.jpg'))
    db.session.commit()
```

试一下：

```
$ docker-compose run users-service python manage.py seed_db

```

最后确保这次能够在浏览器中看到JSON数据了[http://YOUR-IP:5001/reports](http://your-ip:5001/reports。