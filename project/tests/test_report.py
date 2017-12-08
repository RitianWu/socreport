# project/tests/test_report.py


import json

from project import db
from project.api.models import Report
from project.tests.base import BaseTestCase


def add_report(name, url):
    report_object = Report(name=name, url=url)
    db.session.add(report_object)
    db.session.commit()
    return report_object


class TestReportService(BaseTestCase):
    """Tests for the Report Service."""

    def test_report(self):
        """Ensure the /ping route behaves correctly."""
        response = self.client.get('/ping')
        data = json.loads(response.data.decode())
        self.assertEqual(response.status_code, 200)
        self.assertIn('pong!', data['message'])
        self.assertIn('success', data['status'])

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

    def test_single_report(self):
        """Ensure get single report behaves correctly."""
        # report = Report(name='测试Report添加', url='http://wiosky.com/test.jpg')
        report_object = add_report('测试Report添加', 'http://wiosky.com/test.jpg')
        # db.session.add(report_object)
        # db.session.commit()
        with self.client:
            response = self.client.get('/reports/{report_id}'.format(report_id=report_object.id))
            data = json.loads(response.data.decode())
            self.assertEqual(response.status_code, 200)
            self.assertIn('success', data['status'])
            self.assertIn('Query success', data['message'])
            self.assertIn('测试Report添加', data['data']['name'])
            self.assertIn('http://wiosky.com/test.jpg', data['data']['url'])
            self.assertTrue('create_time' in data['data'])

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
