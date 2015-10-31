
import sys
import colorsys
import math
import datetime
import threading
from functools import partial
from time import sleep
from logging import FileHandler, Formatter, getLogger, DEBUG
from flask import Flask, request, Response, make_response, jsonify
from flask.ext.autodoc import Autodoc

from constants import *

from LedControl import LEDController, LEDMaster


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

def getColor(**kwargs):
	if 'rgb' in kwargs.keys():
		return splitrgb(kwargs['rgb'])
	if all(v in 'rgb' for v in kwargs.keys()):
		return int(kwargs['r']), int(kwargs['g']), int(kwargs['b'])
	else:
		raise Exception("Cannot decode color.")




app = Flask(__name__)
auto = Autodoc(app)
master = LEDMaster()

loggers = [app.logger]
file_handler = FileHandler('flask.log')
file_handler.setLevel(DEBUG)
file_handler.setFormatter(Formatter('%(asctime)s %(levelname)8s [%(filename)s/%(funcName)s:%(lineno)d] - %(message)s'))

for logger in loggers:
	logger.handlers = []
	logger.addHandler(file_handler)



###############
##Development
###############


@app.route('/test')
def testthread():
	c = LEDController('pixel'+str(datetime.datetime.now()), range(100))
	master.add(c, c.setColor, (255, 255, 0))
	c = LEDController('strobe', range(100))
	master.add(c, c.strobe, (2, ))
	return getResponse()


@app.route('/dev/logs/debug')
def debuglogs():
	with open('flask.log') as f:
		return "/n".join(f.read().split('/n')[-5:])
	

@app.route("/areas")
@auto.doc()
def ranges():
	'''Returns a json of given ranges'''
	return getResponse(jsonify(areas=AREAS.keys()), 200)
	

@app.route("/off")
@auto.doc()
def off():
	'''switch everything off'''
	pass
	return getResponse()

@app.route("/running")
def getThreads():
	return str([i.name for i, t in master.controllers])

@app.route("/brightness/<float:brightness>", methods=["POST"])
@auto.doc()
def brightness(brightness):
	#TODO ws.brightness(brightness)
	return getResponse()


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

	## get the color
	r,g, b = getColor(**post)
	app.logger.debug("Got Color.")
	## get the pos
	pos = getPosition(**post)
	app.logger.debug("Got Position.")

	c = LEDController('pixel'+str(datetime.datetime.now()), pos)
	
	master.add(c, c.setColor, (r, g, b))
	
	return getResponse()
	


@app.route("/scene", methods=['POST'])
@auto.doc()
def set(range_id, scene_id):
	pass




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
	#make_pulsate(pos)

	return getResponse()


@app.route("/effect/strobe", methods=['POST', 'OPTIONS'])
def strobe():
	if request.method == 'OPTIONS':
		return getResponse()

	post = request.get_json()
	pos = getPosition(**post)
	frequency = post["frequency"]

	c = LEDController('strobe', pos)
	master.add(c, c.strobe, (frequency, ))
	return getResponse()

@app.route("/stop/<cname>")
def stop_thread(cname):
	out = ''
	for index, (i, t) in enumerate(master.controllers):
		if i.name == cname:
			i.finishThread()
			master.controllers.pop(index)
			return getResponse("finished")
	return getResponse("nothing finished", 200)



@app.route('/docs')
def documentation():
	return auto.html()

if __name__ == '__main__':
	
	app.run(host='0.0.0.0', port=9000, debug=True)
	