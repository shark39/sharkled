
import sys
import logging
import colorsys
import math
from functools import partial
from time import sleep
from flask import Flask, request, Response, make_response, jsonify
from flask.ext.autodoc import Autodoc

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


def getResponse(jsondata='', status=200):
	resp = make_response(jsondata, status)
	resp.headers['Access-Control-Allow-Origin'] = '*'
	resp.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
	resp.headers['Access-Control-Allow-Headers'] = "Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With"
	return resp


def getPosition(areas=None, indexes=None, **kwargs):
	pos = []
	if areas:
		app.logger.debug("Got Areas from Request: " + str(areas))
		for a in areas:
			pos += AREAS[a]
	if indexes:
		app.logger.debug("Got range from Request: " + str(indexes))
		try: 
			pos += eval('range(LEDS_COUNT)'+ indexes)
		except Exception as ex:
			app.logger.debug("Cannot parse range. " + str(ex))
	return pos

app = Flask(__name__)
auto = Autodoc(app)

###############
##Development
###############


@app.route('/dev/logs/debug')
def debuglogs():
	pass

@app.route("/areas")
@auto.doc()
def ranges():
	'''Returns a json of given ranges'''
	return getResponse(jsonify(areas=AREAS.keys()), 200)
	


@app.route("/off")
@auto.doc()
def off():
	'''switch everything off'''
	ws.off()
	return getResponse('', 200)


@app.route("/brightness/<float:brightness>", methods=["POST"])
@auto.doc()
def brightness(brightness):
	ws.brightness(brightness)
	return getResponse('', 200)


@app.route("/pixel", methods=['POST', 'OPTIONS'])
@auto.doc()
def set_pixel():
	'''Parameters: 
		rgb: Integer between 0x0 and 0xFFFFFF
		or: r, g, b: int between 0x and 0xFF each
		and: areas: comma seperated list with names of areas 
		or: indexes: python syntax for positions for leds
		''' 
	if request.method == 'OPTIONS':
		return getResponse()

	post = request.get_json()

	if not ('rgb' in post or all([v in post.keys() for v in 'rgb'])):
		return 'Please include rgb or r and g and b in your form parameters', 400
	## get the color
	if 'rgb' in post:
		rgb = int(post['rgb'])
		r, g, b = splitrgb(rgb) 
	else:
		r, g, b = map(int, [post[v] for v in 'rgb'])
	## get the pos
	print("pixel")
	pos = getPosition(**post)
	app.logger.debug("Got Position.")
	for p in pos:
		ws.set_pixel(p, r, g, b)
	ws.show()
	return getResponse()
	


@app.route("/scene", methods=['POST'])
@auto.doc()
def set(range_id, scene_id):
	pass



def make_pulsate(pos):
	for t in range(300): ## damits stoppt
		for i, p in enumerate(pos):
			## in hsv umrechnen
			h, s, v = colorsys.rgb_to_hsv(*ws.get_pixel(p))
			## mit sin(ID) multiplizieren
			new_h = (math.sin(i*2*math.pi/len(pos))+1)/3*h
			ws.set_pixel_hsv(p, new_h, s, v)
		ws.show()
		sleep(0.1)



	## zurueckumrechnen



@app.route("/effect/pulsate", methods=['POST', 'OPTIONS'])
def pulsate():
	'''Adds a pulsation to the current light
	Parameter: 
	areas or indexes

	speed/frequency
	intensity
	patter (default:sinus)
	parameter: v or s (Helligkeit oder Saettigung)'''
	if request.method == 'OPTIONS':
		return getResponse()

	post = request.get_json()
	pos = getPosition(**post)
	make_pulsate(pos)

	return getResponse()


def make_strobe(pos):
	leds = [ws.get_pixel(d) for d in pos]
	for i in range(300):
		ws.off()
		sleep(0.1)
		for p, d in zip(pos, leds):
			ws.set_pixel(p, *d)
		ws.show()	
		sleep(0.1)

@app.route("/effect/strobe", methods=['POST', 'OPTIONS'])
def strobe():
	if request.method == 'OPTIONS':
		return getResponse()

	post = request.get_json()
	pos = getPosition(**post)

	#start_new_thread(make_strobe, (pos,))
	make_strobe(pos)
	return getResponse()


@app.route('/docs')
def documentation():
	return auto.html()

if __name__ == '__main__':
	
	if RPI:
		app.run(host='0.0.0.0', port=9000, debug=True)
	else:
		start_new_thread(ws.win.mainloop, ())
		
		start_new_thread(partial(app.run, '0.0.0.0', port=9000), ()) 
		while True:
			pass
			
