import signal
import sys
import colorsys
import math
import datetime
import inspect
import collections 
import jellyfish
from functools import partial
from time import sleep
from logging import FileHandler, Formatter, getLogger, DEBUG
from flask import Flask, request, Response, make_response, jsonify
from flask.ext.autodoc import Autodoc
from functools import wraps
from constants import *
from colornames import COLORS

from LedControl import LEDController, LEDMaster
from parameter_validation import Validator
from natural_language_parser import NLP 

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
		#app.logger.debug("Got range from Request: " + str(indexes))
		try: 
			pos += eval('range(LEDS_COUNT)'+ indexes)
		except Exception as ex:
			pass
			#app.logger.debug("Cannot parse range. " + str(ex))
	return pos


app = Flask(__name__)
auto = Autodoc(app)
master = LEDMaster()

#loggers = [app.logger]
#file_handler = FileHandler('flask.log')
#file_handler.setLevel(DEBUG)
#file_handler.setFormatter(Formatter('%(asctime)s %(levelname)8s [%(filename)s/%(funcName)s:%(lineno)d] - %(message)s'))

#for logger in loggers:
#	logger.handlers = []
#	logger.addHandler(file_handler)



###############
##Development
###############


### decoraters

def add_response_headers(headers={}):
    """This decorator adds the headers passed in to the response"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            resp = make_response(f(*args, **kwargs))
            h = resp.headers
            for header, value in headers.items():
                h[header] = value
            return resp
        return decorated_function
    return decorator


def browser_headers(f):
    """This decorator is awesome"""
    @wraps(f)
    @add_response_headers({'Access-Control-Allow-Origin': '*', \
    	'Access-Control-Allow-Methods': 'GET,POST,PUT,DELETE,OPTIONS', \
    	'Access-Control-Allow-Headers': 'Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With'})
    def decorated_function(*args, **kwargs):
        return f(*args, **kwargs)
    return decorated_function



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

#############################
## GETTERS			       ##
#############################

@app.route("/leds")
@browser_headers
@auto.doc()
def getLeds():
	'''array with 3-tuple of the current color of the leds'''
	return getResponse(jsonify(leds=master.getLeds()))

@app.route("/areas")
@browser_headers
@auto.doc()
def ranges():
	'''Returns a list of given ranges'''
	return getResponse(jsonify(areas=AREAS.keys()), 200)

@app.route("/effects")
@browser_headers
@auto.doc()
def effects():
	'''list with all available effects and default parameters'''
	return getResponse(jsonify(effects=LEDMaster.getEffects()), 200)

	
@app.route("/running")
@browser_headers
@auto.doc()
def getControllers():
	'''id, name and parameters of all running effects'''
	controllers = [{"id": cid, "name" : c.name, "parameters": c.parameters} for cid, c in master.controllers.items()]
	return getResponse(jsonify(controllers=controllers), 200)


#############################
## WORKFLOW 		       ##
#############################

@app.route("/effect/<name>", methods=['POST', 'OPTIONS'])
@browser_headers
def effect(name):
	'''Add New Effect. Name is equally to name defined in class LedEffect'''
	post = request.get_json()
	warnings = []
	## do validation
	## validation for all
	for f in [Validator.areas, Validator.z]:
		validation = f(post)
		warnings += validation.warnings
		post = validation.post

	## validation for specific
	validations = {"color": [lambda x: Validator.color(x, ['color'])]}
	if name in validations:
		for f in validations[name]:
			validation = f(post)
			warnings += validation.warnings
			post = validation.post
	else:
		warnings.append("No Validator defined for effect parameters")
	

	### outsource the following code in validators
	for k in post.iterkeys():
		if name == 'sequence' and k == 'fadespeed' and post['fadespeed'] < 1:
			post[k] = post[k] * post['interval'] # make fadespeed from relative to absolute depending on interval 
		if name == 'sequence' and k == 'sequence':
			post[k] = map(lambda x: x+[1] if len(x) == 3 else x, post[k])

		if name == 'chase':
			if post.get('width') and post.get('width') < 1: 
				pass #post['width'] = int(post['width'] * post['pos'])
			if post.get('soft') and post['soft'] < 1: 
				post['soft'] = int(post['soft'] * post['width'])
		if name == 'pulsate':
			if post.get('wavelength') <= 1:
				pass #wavelength = int(post.get('wavelength') * length)

	lid = master.add(name=name, parameters=post)
	return jsonify(id=lid, name=name, parameters=master.getControllerParameters(lid), warnings=warnings), 201


@app.route("/reset", methods=['POST', 'OPTIONS'])
@auto.doc()
def reset():
	'''finish all led controllers and set color and mask to default'''
	if request.method == 'OPTIONS':
		return getResponse()
	master.reset()
	return getResponse('', 204)


@app.route("/effect/adjust/<int:cid>", methods=['POST', 'OPTIONS'])
@browser_headers
def adjust(cid):
	post = request.get_json()

	controller = master.getController(cid)
	controller.parameters = post
	return getResponse('', 204)


@app.route("/stop/<int:cid>", methods=["POST"])
@auto.doc()
def stop_controller():
	'''stopps the running controller
	Parameters: name or id'''
	app.logger.debug("finish controller %i" %cid)
	master.finishControllerById(cid) 
	return getResponse("finished", 200)


@app.route("/nlp/effect", methods=['GET', 'OPTIONS', 'POST'])
@browser_headers
def natural_language_effect():
	post = request.get_json() 
	if not post:
		return getResponse()
	## parsing response
	text = post.get('text')

	nlp = NLP()
	interpretation = nlp.process(text)
	areas = Validator.areas({"areas": interpretation.areas}).post["areas"]
	z = Validator.z(interpretation.parameters).post['z']
	parameters = interpretation.parameters
	parameters['z'] = z
	parameters['areas'] = areas
	
	##add effect
	lid = master.add(name=interpretation.effect, parameters=parameters)
	effectreturn =  dict(id=lid, name=interpretation.effect, parameters=master.getControllerParameters(lid))

	return getResponse(jsonify(interpretation={}, effect=effectreturn), 201) 



#################
#Docs&Help     ##
#################

@app.route('/docs')
def documentation():
	return auto.html()


@app.route('/help')
def showEffects():
	out = ''
	for effect in LEDMaster.getEffects():
		out += '<h1>' + effect['name'] + '</h1>'
		desc = LEDMaster.getDescription(effect['name'])
		desc = desc.replace('Description:', '<h4>Description</h4>')
		desc = desc.replace('Parameters:', '<h4>Parameters</h4>')
		pi = desc.find('<h4>Parameters</h4>')+len('<h4>Parameters</h4>')
		pdesc = ''
		for pname_pdesc in desc[pi:].split('\n'):
			if pname_pdesc.count(':') == 1:
				pname, pdes = pname_pdesc.split(':')
				pdesc += '<b>%s:</b> %s <br>' %(pname.strip(), pdes) 
		out += desc[:pi] + pdesc
	return out


if __name__ == '__main__':
	def signal_handler(signal, frame):
	    master.finish = True
	    sys.exit(0)
	signal.signal(signal.SIGINT, signal_handler)
	if sys.platform == 'win32':
		debug = True
	else:
		debug = False
	app.run(host='0.0.0.0', port=9000, debug=debug)
			