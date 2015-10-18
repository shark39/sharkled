
import sys
from flask import Flask, request, Response, make_response
from flask.ext.autodoc import Autodoc
#from flask.ext.api import status

if sys.platform == 'linux2':
	## using raspberry
	RPI = True
	import unicornhat as ws
else:
	from thread import start_new_thread
	from wsscreen import Stripe 
	ws = Stripe() 
	RPI = False


def mergergb(r, g, b):
	return str('%6x' %((r << 16) + (g << 8) + b)).replace(' ', '0')

def splitrgb(rgb):
	return rgb>>16, (rgb>>8) & 255, rgb & 255 



app = Flask(__name__)
auto = Autodoc(app)


@app.route("/range")
@auto.doc()
def ranges():
	'''Returns a list of given ranges'''
	return ["vorne", "tv", "pascals zimmer"]

@app.route("/pixel", methods=['OPTIONS'])
def what():
	resp = make_response()
	resp.headers['Access-Control-Allow-Origin'] = '*'
	resp.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
	resp.headers['Access-Control-Allow-Headers'] = "Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With"
	return resp


@app.route("/pixel", methods=['POST'])
@auto.doc()
def set_pixel():
	#if not ('rgb' in request.form or all([v in request.form for v in 'rgb'])):
	#	return 'Please include rgb or r and g and b in your form parameters', 400
	#if 'rgb' in request.form:
	post = request.get_json()
	print post
	rgb = int(post['rgb'])
	pixel = post['pixel']
	for p in eval('range(150)'+pixel):
		print p
		ws.set_pixel(p, splitrgb(rgb)[0], splitrgb(rgb)[1], splitrgb(rgb)[2])
	ws.show()
	resp = make_response()
	resp.headers['Access-Control-Allow-Origin'] = '*'
	resp.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
	resp.headers['Access-Control-Allow-Headers'] = "Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With"
	return resp
	



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
			
