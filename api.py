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

from constants import *
from colornames import COLORS

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
		#app.logger.debug("Got range from Request: " + str(indexes))
		try: 
			pos += eval('range(LEDS_COUNT)'+ indexes)
		except Exception as ex:
			pass
			#app.logger.debug("Cannot parse range. " + str(ex))
	return pos

def getColor(**kwargs):
	#app.logger.debug("Got information to decode for color" + str(kwargs))
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

@app.route("/effects")
@auto.doc()
def effects():
	return getResponse(jsonify(effects=LEDMaster.getEffects()), 200)



	
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


####################
## Effects
####################



@app.route("/effect/<name>", methods=['POST', 'OPTIONS'])
def effect(name):
	if request.method == 'OPTIONS':
		return getResponse()
	post = request.get_json()
	if not post:
		post = {"areas": ["all"]}
	for k in post.iterkeys():
		if k == 'color':
			if len(post[k]) == 3: 
				post[k].append(1) ## add alpha value for color

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
		
		
	## add default z-index
	if 'z' not in post:
		post['z'] = 0
	## add default area
	if 'areas' not in post:
		post['areas'] = ['all']
	if type(post["areas"]) == str:
		post["areas"] = [post["areas"]]

	for i, a in enumerate(post['areas']):
		post['areas'][i] = a.capitalize()


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


@app.route("/jellyfish/effect", methods=['GET', 'OPTIONS', 'POST'])
def natural_language_effect():
	if request.method == 'OPTIONS':
		return getResponse()
	post = request.get_json() or 'Wand chase'
	## parsing response
	threshold = 0.75
	text = post.get('text')
	
	## find areas
	areas = []
	words = text.split()
	for i, word in enumerate(words): ## TODO detect stuff like Balken1, Wand2
		for a in AREAS:
			if a[-1] in '1234':
				continue ## TODO detect if number is attached
			if jellyfish.jaro_distance(unicode(a), unicode(word)) > threshold and a not in areas:
				areas.append(a)
	
	## find effect name
	## word with highest match and before keyword parameters
	choices = [e['name'] for e in LEDMaster.getEffects()]
	best_match_effect = collections.namedtuple('Match', 'effect chance')
	best_match_effect.chance = 0
	parameters_i = 0 ## store the index of parameters to continue faster
	for effect in choices:
		for i, word in enumerate(words):
			if jellyfish.jaro_distance(u"parameter", unicode(word)) > threshold:
				parameters_i = i
				break
			else:
				match = jellyfish.jaro_distance(unicode(effect), unicode(word)) 
				if match > best_match_effect.chance:
					best_match_effect.chance = match
					best_match_effect.effect = effect
				continue ## prevent from breaking out of the second loop
			break

	## detect parameters
	parameters = LEDMaster.getDefaultParameters(best_match_effect.effect) ## always load default 
	if parameters_i > 0: ## no parameters
		for i, word in enumerate(words[parameters_i+1:-1], start=parameters_i+1):
			for j, p in enumerate(parameters.keys()):
				match = jellyfish.jaro_distance(unicode(p), unicode(word)) 
				if match > threshold:
					##convert value after keyword to correct type
					correct_type = type(parameters[p])
					if correct_type == list: ## assume that we have a color here
							best_match_color = collections.namedtuple('Match', 'index chance')
							best_match_color.chance = 0
							for j, c in enumerate(COLORS):
								match = jellyfish.jaro_distance(unicode(c['name']), unicode(words[i+1])) 
								if match > threshold and match > best_match_color.chance:
									best_match_color.chance = match
									best_match_color.index = j
							if best_match_color.chance > 0:
								rgb = map(lambda x: x/255.0, list(eval(COLORS[best_match_color.index]['rgb']))) + [1]
								parameters[p] = rgb
		
					else:	
						try: 
							value = correct_type(words[i+1])
						except IndexError:
							break ## last index
						except:
							print "exception"
							
							print "Failed to decode ", words[i], words[i+1]
						else:
							parameters[p] = value
		
	if not areas:
		parameters["areas"] = ["All"]
	else:
		parameters["areas"] = areas

	inpterpretation = {"effect": best_match_effect.effect, "areas": areas, "parameters": parameters}
	try:
		inpterpretation["color"] = COLORS[best_match_color.index]['name']
	except NameError:
		pass ## no color in parameters
	except:
		pass ## something else

	##add effect
	lid = master.add(name=best_match_effect.effect, parameters=parameters)
	effectreturn =  dict(id=lid, name=best_match_effect.effect, parameters=master.getControllerParameters(lid))

	return getResponse(jsonify(inpterpretation=inpterpretation, effect=effectreturn), 201) 



@app.route('/docs')
def documentation():
	return auto.html()

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
		
	