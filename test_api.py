import unittest

from flask import Flask, jsonify, request, url_for, abort, send_from_directory, render_template, send_file, Response, make_response
from api import app


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



	def test_get_all_leds(self):
		self.test_app.open(self.api_url_for('getLeds'), 'GET')




if __name__ == '__main__':
	unittest.main()

