import unittest
import json
from flask import Flask, jsonify, request, url_for, abort, send_from_directory, render_template, send_file, Response, make_response
from api import app
from constants import *


class APITestCase(unittest.TestCase):

    ##############################
    # setup
    ##############################

    def setUp(self):
        self.test_app = app.test_client()

    def tearDown(self):
        pass

    def api_url_for(self, endpoint, **kwargs):
        with app.test_request_context('/'):
            return url_for(endpoint, **kwargs)

    def request(self, method, url, **kwargs):
        headers = kwargs.get('headers', {})

        headers['Content-Type'] = 'application/json'

        kwargs['headers'] = headers

        return self.test_app.open(url, method=method, **kwargs)

    ##############################
    # tests
    ##############################

    def test_get_all_leds(self):
        response = self.test_app.open(self.api_url_for('getLeds'), 'GET')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data["leds"]) == LEDS_COUNT

    def test_effect_color(self):
        response = self.request('POST', '/effect/color', data={"areas": "all"})
        print response.status_code
        #assert response.status_code == 201
        data = json.loads(response.data)
        print data


if __name__ == '__main__':
    unittest.main()
