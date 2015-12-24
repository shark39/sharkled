import signal
import sys
import colorsys
import math
import datetime
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

	return getResponse(jsonify(controllers=master.controllers.items()), 200)


@app.route("/brightness/<float:brightness>", methods=["POST"])
@auto.doc()
def brightness(brightness):
	#TODO ws.brightness(brightness)
	return getResponse()


@app.route("/stop/<int:cid>", methods=["POST"])
@auto.doc()
def stop_controller():
	'''stopps the running controller
	Parameters: name or id'''
	app.logger.debug("finish controller %i" %cid)
	master.finishControllerById(cid) 
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

	lid = master.add(name='color', pos=pos, bufferType='color', function=LEDController.setColor, parameters={'r': r, 'g': g, 'b': b})
	return  getResponse(jsonify(id=lid, name='color'), 201)


####################
## Effects
####################



@app.route("/effect/<name>", methods=['POST', 'OPTIONS'])
def effect(name):
	if request.method == 'OPTIONS':
		return getResponse()
	post = request.get_json()
	for k in post.iterkeys():
		if k == 'color':
			if len(post[k]) == 3: 
				post[k].append(1) ## add alpha value for color

		if name == 'sequence' and k == 'fadespeed':
			post[k] = post[k] * post['interval'] # make fadespeed from relative to absolute depending on interval 
		if name == 'sequence' and k == 'sequence':
			post[k] = map(lambda x: x+[1] if len(x) == 3 else x, post[k])

	## add default z-index
	if 'z' not in post:
		post['z'] = 0
	## add default area
	if 'areas' not in post:
		post['areas'] = 'all'

	lid = master.add(name=name, parameters=post)
	return getResponse(jsonify(id=lid, name=name, parameters=master.getControllerParameters(lid)), 201)


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
	def signal_handler(signal, frame):
	    master.finish = True
	    sys.exit(0)
	signal.signal(signal.SIGINT, signal_handler)
	app.run(host='0.0.0.0', port=9000, debug=False)
		
	