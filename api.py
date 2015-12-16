
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
	app.logger.debug("Got information to decode for color" + str(kwargs))
	if 'rgb' in kwargs.keys():
		return map(lambda x: 1.0*x/255, splitrgb(kwargs['rgb']))
	if 'r' in kwargs.keys() and 'g' in kwargs.keys() and 'b' in kwargs.keys():
		if any(map(lambda x: x > 1, [float(kwargs['r']), float(kwargs['g']), float(kwargs['b'])])):
			return float(kwargs['r'])/255, float(kwargs['g'])/255, float(kwargs['b'])/255
		else:
			return float(kwargs['r']), float(kwargs['g']), float(kwargs['b'])
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



@app.route('/thingsee', methods=['POST'])
def thingsee():
	return getResponse()
	

@app.route('/dev/logs/debug')
def debuglogs():
	with open('flask.log') as f:
		return "/n".join(f.read().split('/n')[-5:])

@app.route('/dev/logs/requests')
def requestlogs():
	with open('nohup.out') as f:
		return "/n".join(f.read().split('/n')[-5:])

@app.route("/debugger")
def dev():
	raise

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is None:
        raise RuntimeError('Not running with the Werkzeug Server')
    func()

@app.route('/shutdown', methods=['POST'])
def shutdown():
    shutdown_server()
    return 'Server shutting down...'
	
###############################
##############################
###############################	

###############################
## BASICS			###########
###############################


@app.route("/leds")
def getLeds():
	return getResponse(jsonify(leds=master.getLeds()))

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

	return getResponse(jsonify(threads=master.enumerateControllers()), 200)


@app.route("/brightness/<float:brightness>", methods=["POST"])
@auto.doc()
def brightness(brightness):
	#TODO ws.brightness(brightness)
	return getResponse()


@app.route("/stop", methods=["POST"])
@auto.doc()
def stop_thread():
	'''stopps the running controller
	Parameters: name or id'''
	post = request.get_json()
	app.logger.debug("stop %s" %str(post))
	if 'id' in post.keys():
		app.logger.debug("finish controller %s" %str(post['id']))
		master.finishController(cid=int(post['id'])) 
	if 'name' in post.keys():
		master.finishController(name=post["name"])
	return getResponse("finished", 200)


#################
#################
#################

@app.route("/color", methods=['POST', 'OPTIONS'])
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

	lid = master.add(name='color', pos=pos, bufferType='color', function=LEDController.setColor, args=(r, g, b))
	return  getResponse(jsonify(id=lid, name='color'), 201)


####################
## Effects
####################


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

	lid = master.add(name='effect-pulse', pos=pos, bufferType='mask', function=LEDController.pulsate)
	return getResponse(jsonify(id=lid, name='effect-pulse'), 201)



@app.route("/effect/strobe", methods=['POST', 'OPTIONS'])
def strobe():
	if request.method == 'OPTIONS':
		return getResponse()

	post = request.get_json()
	pos = getPosition(**post)
	try:
		frequency = float(post["frequency"])
	except:
		return getResponse('invalid parameter for frequency', 400)

	lid = master.add(name='effect-strobe', pos=pos, bufferType='mask', function=LEDController.strobe, args=(frequency, ))
	return getResponse(jsonify(id=lid, name='effect-strobe'), 201)


@app.route("/effect/chase", methods=['POST', 'OPTIONS'])
def chase():
	if request.method == 'OPTIONS':
		return getResponse()

	post = request.get_json()
	pos = getPosition(**post)

	pause = post["pause"]
	width = post["width"]
	lid = master.add(name='effect-chase', pos=pos, bufferType='mask', function=LEDController.chase, args=(pause, width))
	return getResponse(jsonify(id=lid, name='effect-chase', parameters=master.getControllerParameters(lid)), 201)


@app.route("/effect/partyblink", methods=['POST', 'OPTIONS'])
def partyblink():
	if request.method == 'OPTIONS':
		return getResponse()

	post = request.get_json()
	pos = getPosition(**post)

	pause = post["pause"]
	width = post["width"]
	lid = master.add(name='effect-partyblink', pos=pos, bufferType='color', function=LEDController.partyblink, args=(pause, width))
	return getResponse(jsonify(id=lid, name='effect-partyblink', parameters=master.getControllerParameters(lid)), 201)



## reset
@app.route("/reset", methods=['POST', 'OPTIONS'])
@auto.doc()
def reset():
	'''finish all led controllers and set color and mask to default'''
	if request.method == 'OPTIONS':
		return getResponse()
	master.reset()
	return getResponse('', 204)

@app.route("/clear", methods=['POST', 'OPTIONS'])
def clear():
	'''set mask and color to default'''
	if request.method == 'OPTIONS':
		return getResponse()
	master.clear()
	return getResponse('', 204)


@app.route("/adjust/<int:cid>", methods=['POST', 'OPTIONS'])
def adjust(cid):
	if request.method == 'OPTIONS':
		return getResponse()

	post = request.get_json()

	controller = master.getController(cid)
	controller.parameters = post
	return getResponse('', 204)

@app.route('/docs')
def documentation():
	return auto.html()

if __name__ == '__main__':
	
	app.run(host='0.0.0.0', port=9000, debug=False)
	