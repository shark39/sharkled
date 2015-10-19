
import sys
import logging
from flask import Flask, request, Response, make_response, jsonify
from flask.ext.autodoc import Autodoc
from flask.ext.cors import CORS
#from flask.ext.api import status

from constants import *

if sys.platform == 'linux2':
	## using raspberry
	RPI = True
	import unicornhat as ws
else:
	from thread import start_new_thread
	from wsscreen import Stripe 
	ws = Stripe() 
	RPI = False


logging.basicConfig(filename='debug.log',level=logging.DEBUG, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')



def mergergb(r, g, b):
	return str('%6x' %((r << 16) + (g << 8) + b)).replace(' ', '0')

def splitrgb(rgb):
	return rgb>>16, (rgb>>8) & 255, rgb & 255 


def getResponse(jsondata, status):
	resp = make_response(jsondata, status)
	resp.headers['Access-Control-Allow-Origin'] = '*'
	resp.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
	resp.headers['Access-Control-Allow-Headers'] = "Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With"
	return resp



app = Flask(__name__)
auto = Autodoc(app)
#cors = CORS(app, resources={r"/*": {"origins": "*"}})


@app.route("/areas")
@auto.doc()
def ranges():
	'''Returns a json of given ranges'''
	return getResponse(jsonify(areas=AREAS.keys()), 200)
	

@app.route("/pixel", methods=['OPTIONS'])
def what():
	resp = make_response()
	resp.headers['Access-Control-Allow-Origin'] = '*'
	resp.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
	resp.headers['Access-Control-Allow-Headers'] = "Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With"
	return resp


@app.route("/off")
@auto.doc()
def off():
	'''switch everything off'''
	ws.off()
	return ''



@app.route("/pixel", methods=['POST'])
@auto.doc()
def set_pixel():
	'''Parameters: 
		rgb: Integer between 0x0 and 0xFFFFFF
		or: r, g, b: int between 0x and 0xFF each
		and: areas: comma seperated list with names of areas 
		or: range: python syntax for positions for leds
		''' 
	post = request.get_json()
	if not ('rgb' in post or all([v in post.keys() for v in 'rgb'])):
		return 'Please include rgb or r and g and b in your form parameters', 400
	## get the color
	if 'rgb' in post:
		rgb = int(post['rgb'])
		r, g, b = splitrgb(rgb) 
	else:
		r, g, b = map(int, [post[v] for v in 'rgb'])
	print("Color set.")
	## get the pos
	if 'areas' in post:
		print(post['areas'])
		pos = []
		for a in post["areas"]:
			pos += AREAS[a]
	if 'range' in post:
		print('range(LEDS_COUNT)'+ post["range"])
		try: 
			pos = eval('range(LEDS_COUNT)'+ post["range"])
		except Exception as ex:
			print(ex)

	print(pos)
	print("Position set.")
	for p in pos:
		ws.set_pixel(p, r, g, b)
	ws.show()
	return getResponse('', 200)
	


@app.route("/scene", methods=['POST'])
@auto.doc()
def set(range_id, scene_id):
	pass

@app.route('/docs')
def documentation():
	return auto.html()

if __name__ == '__main__':
	if RPI:
		app.run(host='0.0.0.0', port=9000, debug=True)
	else:
		start_new_thread(ws.win.mainloop, ())
		app.port = 9000
		start_new_thread(app.run, ('0.0.0.0',)) 
		while True:
			pass
			
