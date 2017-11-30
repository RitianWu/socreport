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
