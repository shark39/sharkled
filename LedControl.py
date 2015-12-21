import threading
from threading import Thread
import time
from  datetime import datetime
from functools import partial
import sys
import logging
import random
import math
import colorsys
import collections

from timer import Timer


if sys.platform in ['linux2', 'linux']:
	## using raspberry
	RPI = True
	import unicornhat as ws
else:
	from wsscreen import Stripe 
	ws = Stripe() 
	RPI = False
	t = Thread(target=ws.win.mainloop, args=())
	#t.start()


logging.basicConfig(filename='ledcontrol.log',level=logging.DEBUG)

class LEDMaster:

	def __init__(self):
		
		self.sleeptime = 30 #ms
		self.controllers = {}
		self.mask = ws.LED_COUNT*[1]
		self.color = ws.LED_COUNT*[(0,0,0)]
		self.finish = False
		self.bufferThread = Thread(target=self.writeBuffer)
		self.bufferThread.start()
		

	def add(self, name, pos, bufferType, function, parameters={}):
		compare = lambda x, y: collections.Counter(x) == collections.Counter(y)
		id = -1
		for i, controller in self.controllers.iteritems():
			if controller.name == name and compare(pos,controller.pos):
				controller.parameters = parameters
				id = controller.id
		if id < 0:
			c = LEDController(name, pos, bufferType, function, parameters, self)
			self.controllers[c.id] = c
			id = c.id
			logging.debug("added new controller %s" %str(self.controllers))
		return id

	def getController(self, cid):
		return self.controllers[cid]

	def getControllerParameters(self, cid):
		return self.controllers[cid].parameters

	def reset(self):
		self.controllers = {}
		self.id = 0
		self.clear()

	def clear(self):
		self.mask = ws.LED_COUNT*[1]
		self.color = ws.LED_COUNT*[(0,0,0)]


	def enumerateControllers(self):
		return self.controllers.iteritems()

	def finishControllerById(self, cid):
		del self.controllers[cid]

	def getLeds(self):
		out = []
		for i in range(ws.LED_COUNT):
			out.append(ws.get_pixel(i))
		return out
				
	def writeBuffer(self):
		print 'start write buffer'
		while True:
			timestamp = int(time.time()*1000)
			mixTypeRank = ['min', 'avg', 'max', 'notme', 'onlyme']
			controllers = sorted(self.controllers.iteritems(), key=lambda (i,c): mixTypeRank.index(c.mixType))
			#because of thread problems fetching before iterating is important
			for i, controller in controllers:
				if controller.paused: pass
				buffer = controller.effect(timestamp + controller.offset)
				for i, pos in enumerate(controller.pos):
			#		if controller.bufferType == 'mask':
			#			self.mask[pos] = buffer[i]
			#		if controller.bufferType == 'color':
				#		self.color[pos] = buffer[i]
				#for i, value in enumerate(buffer):
					if controller.bufferType == 'mask':
						if controller.mixType == 'notme':
							if(self.mask[pos] == -1): self.mask[pos] = buffer[i]
						elif controller.mixType == 'onlyme':
							self.mask[pos] = buffer[i]
						elif controller.mixType == 'max':
							self.mask[pos] = max(self.mask[pos],buffer[i])
						elif controller.mixType == 'min':
							self.mask[pos] = min(self.mask[pos],buffer[i])
						elif controller.mixType == 'avg':
							self.mask[pos] = (self.mask[pos] + buffer[i]) /2
					elif controller.bufferType == 'color':
						if controller.mixType == 'notme':
							if(self.color[pos] == -1): self.color[pos] = buffer[i]
						elif controller.mixType == 'onlyme':
							self.color[pos] = buffer[i]
						elif controller.mixType == 'max':
							self.color[pos] = max(self.color[pos],buffer[i], key=sum)
						elif controller.mixType == 'min':
							self.color[pos] = min(self.color[pos],buffer[i], key=sum)
						elif controller.mixType == 'avg':
							for colori in range(3):
								self.color[pos][colori] = int((self.color[pos][colori] + buffer[i][colori]) / 2)

			for i, (m, c) in enumerate(zip(self.mask, self.color)):
				ws.set_pixel(i, int(255*c[0]*m), int(255*c[1]*m), int(255*c[2]*m))

			ws.show()
			if self.finish:
				break
			timestampNow = int(time.time()*1000)
			wait = (self.sleeptime - (timestampNow - timestamp))
			if wait > 0:
				time.sleep(wait / 1000.0)
			


			
class LEDController:
	id = 0
	def __init__(self, name, pos, bufferType, function, parameters, master):
		self.name = name
		self.pos = pos
		LEDController.id += 1
		self.bufferType = bufferType
		self.function = function
		self.paused = False
		self.master = master
		self.parameters = parameters
		self.mixType = parameters.get('mixType') or 'max' ## max min avg onlyme notme
		self.offset = parameters.get('offset') or 0
		if self.offset == '-1': self.offset = - int(time.time()*1000)

	def __repr__(self):
		return "LEDController " + self.name + '(' + str(len(self.pos)) + 'leds)'

	def __str__(self):
		return "LEDController " + self.name + '(' + str(len(self.pos)) + 'leds)'

	def set(self, buffer):
		'''write buffer in the corresponding master'''
		for i, p in enumerate(self.pos):
			if self.bufferType == 'color':
				self.master.color[p] = buffer[i]
			elif self.bufferType == 'mask':
				self.master.mask[p] = buffer[i]

	def effect(self, ts):
		return self.function(self, ts)		

	def color(self, ts):
		'''set the color. r, g, b must be between 0 and 1.
		[implementation finished]'''
		color = self.parameters.get('color') or [1,0,0]
		return len(self.pos) * [color]
	
	def mask(self, ts):
		mask = self.parameters.get('mask') or len(self.pos) * [1]
		return mask

	def colorSequence(self, ts):
		'''set the color. r, g, b must be between 0 and 1.
		[implementation finished]'''
		interval = self.parameters.get('interval') or 1000
		sequence = self.parameters.get('sequence') or [[1,0,0],[0,1,0],[0,0,1]]
		fadeSpeed = self.parameters.get('fadeSpeed') or 0
		sinceLast = ts % interval; 

		step = (ts % (interval*len(sequence))) / interval
		color = sequence[step]		
		if fadeSpeed > 0:
			fadeCorrection = (fadeSpeed - sinceLast) / float(fadeSpeed)
			if fadeCorrection >= 0 and fadeCorrection <= 1:
				for i in range(3):
					color[i] = (fadeCorrection * sequence[step-1][i] + (1 - fadeCorrection) * sequence[step][i])
		return len(self.pos) * [color]
		
	def strobe(self, ts):
		'''turn on and off again during a cycle of frequency 
		[implementation finished]'''
		interval = self.parameters['interval']
		brightness = int(ts % interval < (interval / 2))
		return [brightness] * len(self.pos)
		

	def chase(self, ts):
		length = len(self.pos)

		interval = (self.parameters.get('interval') or 1000) * length
		width = self.parameters.get('width') or 5
		softWidth = self.parameters.get('softWidth') or 0
		position = int(length / (interval / float((ts % interval) + 1)))
		mask = [0] * len(self.pos)
		for i in range(-softWidth, width + softWidth):
			mask[(position + i) % length] = 1
			if i < 0:
				mask[(position + i) % length] = 1 + (i / float(softWidth))
			if i >= width:
				mask[(position + i) % length] = 1 - ((i-width) / float(softWidth))
		return mask

	def bucketColor(self, ts):
		length = len(self.pos)
		interval = self.parameters.get('interval') or 1000
		colors = self.parameters.get('colors') or [[1,0,0],[0,1,0],[0,0,1],[0,0,0]]
		bucketSize = self.parameters.get('bucketSize') or 1

		if not hasattr(self, 'lastTs') or self.lastTs + interval < ts:
			colormap = []
			for bucket in range((length/bucketSize) + 1):
				bucketcolor = random.choice(colors)
				for i in range(bucketSize):
					if i < length:
						colormap.append(bucketcolor)
			self.lastTs = ts
			self.colormap = colormap
		return self.colormap

	def rainbow(self, ts):
		length = len(self.pos)
		interval = self.parameters.get('interval') or 1000
		wavelength = self.parameters.get('wavelength') or length
		relativeInterval = ((ts % interval) / float(interval))
		colormap = []
		for i in range(length):
			pos = (i / float(wavelength))
			colormap.append(colorsys.hsv_to_rgb(pos + relativeInterval, 1.0, 1.0))
		return colormap

	def pulsate(self, ts):
		length = len(self.pos)
		interval = self.parameters.get('interval') or 1000
		wavelength = self.parameters.get('wavelength') or length
		relativeInterval = ((ts % interval) / float(interval))
		mask = []
		for i in range(length):
			pos = (i / float(wavelength))
			mask.append(0.5 + 0.5*math.sin((pos + relativeInterval - 0.25) * 2 * math.pi))
		return mask


if __name__ == '__main__':


	master = LEDMaster()
	id1 = master.add(name='color', pos=range(10), bufferType='color', function=LEDController.setColor, parameters = {'r': 1, 'g':0, 'b':0})
	id2 = master.add(name='strobe', pos=range(5), bufferType='mask', function=LEDController.strobe, parameters = {'interval':1000})

	
	# for i in range(300):
	# 	ws.set_pixel(i, 200, 0, 50)
	# 	ws.set_pixel(i+1, 100, 0, 50)
	# 	ws.set_pixel(i+2, 0, 0, 100)
		
	# 	ws.show()
	# 	time.sleep(0.05)
	try:
		while True:
			pass
	except KeyboardInterrupt:
		master.finish = True
			
