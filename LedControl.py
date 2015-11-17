from time import sleep
import threading
from threading import Thread
from time import sleep
from  datetime import datetime
from functools import partial
import sys
import logging


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
		
		self.controllers = {}
		self.id = 0
		self.mask = ws.LED_COUNT*[1]
		self.color = ws.LED_COUNT*[(0,0,0)]
		self.finish = False
		self.bufferThread = Thread(target=self.writeBuffer)
		self.bufferThread.start()
		#self.bufferThread.join()
		## start buffer writing thread


	def add(self, name, pos, bufferType, function, args=(), kwargs={}):

		self.id += 1
		c = LEDController(name, pos, bufferType, self.setLeds)
		t = Thread(target=function, args=(c, ) + args)
		#t.setDeamon()
		t.start()
		self.controllers[self.id] = c
		logging.debug("added new controller %s" %str(self.controllers))
		return self.id

	def getController(self, cid):
		return self.controllers[cid]

	def getControllerParameters(self, cid):
		return self.controllers[cid].parameters

	def reset(self):
		for c in self.controllers.values():
			c.finish = True
		self.controllers = {}
		self.id = 0
		self.mask = ws.LED_COUNT*[1]
		self.color = ws.LED_COUNT*[(0,0,0)]

	def clear(self):
		self.mask = ws.LED_COUNT*[1]
		self.color = ws.LED_COUNT*[(0,0,0)]


	def enumerateControllers(self):
		
		#print[c.name for c, x in self.controllers]
		return self.controllers.items()

	def finishController(self, name=None, cid=None, mode=None):
		droplist = []
		for i, c in self.controllers.items():
			if c.finish:
				continue
			if name and name==c.name:
				droplist.append(c)
			if cid and cid == i:
				droplist.append(c) 
		for c in droplist:
			c.finish = True

	
	def enumerateControllersEffect(self):
		pass


	def enumerateThreads(self):
		return threading.enumerate()

	
	def getLeds(self):
		out = []
		for i in range(ws.LED_COUNT):
			out.append(ws.get_pixel(i))
		return out

	def setLeds(self, controller):
		for i, pos in enumerate(controller.pos):
			if controller.bufferType == 'mask':
				self.mask[pos] = controller.mask[i]
			if controller.bufferType == 'color':
				self.color[pos] = controller.color[i]
				
	def writeBuffer(self):
		while True:
			for i, (m, c) in enumerate(zip(self.mask, self.color)):
				ws.set_pixel(i, int(255*c[0]*m), int(255*c[1]*m), int(255*c[2]*m))
			ws.show()
			if self.finish:
				break
			sleep(0.02)


			
class LEDController:

	def __init__(self, name, pos, bufferType, setfunc):
		self.name = name
		self.pos = pos
		self.bufferType = bufferType
		self.mask = map(lambda x: 1, pos)
		self.color = map(lambda x: (0,0,0), pos)
		self.setfunc = setfunc
		self.timestamp = datetime.now()
		self.finish = False
		self.parameters = {}

	def __repr__(self):
		return "LEDController " + self.name + '(' + str(len(self.pos)) + 'leds)'

	def __str__(self):
		return "LEDController " + self.name + '(' + str(len(self.pos)) + 'leds)'

	def set(self):
		'''call the set function to commit the color or mask array to the master'''
		self.setfunc(self)

	def asParameters(self, **kwargs):
		self.parameters = kwargs

	def getParameters(self, *args):
		out = []
		for a in args:
			out.append(self.parameters[a])
		return out

	def setColor(self, r, g, b):
		'''set the color. r, g, b must be between 0 and 1.
		[implementation finished]'''
		self.color = map(lambda x: (r, g, b), self.color) #len(self.pos) * [(r, g, b)]
		self.set()
		self.finish = True
		

	def strobe(self, frequency):
		'''turn on and off again during a cycle of frequency 
		[implementation finished]'''
		while True:
			self.mask = map(lambda x: 0, self.mask)
			self.set()
			sleep(frequency/2)
			self.mask = map(lambda x: 1, self.mask)	
			self.set()
			sleep(frequency/2)
			if self.finish:
				return

	def chase(self, pause=0.1, width=1):
		'''under development, lauflicht'''
		logging.debug("call chase")
		self.asParameters(pause=pause, width=width)
		self.mask = map(lambda x: 0, self.mask)
		i = 0
		direction = 1
		while True:
			pause, width = self.getParameters('pause', 'width')
			self.mask = map(lambda x: 0, self.mask)
			self.mask[i:i+width] = width*[1]
			if i+width == len(self.mask)-1:
				direction = -1
			if i == 0:
				direction = 1
			i += direction
			if self.finish:
				break
			self.set()
			sleep(pause)




	def pulsate(self):
		'''test, not working (yet)'''
		def conv(i, x):
			if x == 1:
				return 0
			return x+0.1
		while True:
			self.mask = map(conv, enumerate(self.mask))
			sleep(0.5)
			if self.finish:
				break


	def finishThread(self):
		self.finish = True



	## zurueckumrechnen



	def off(self):
		ws.off()


if __name__ == '__main__':


	master = LEDMaster()
	id1 = master.add(name='color', pos=range(10), bufferType='color', function=LEDController.setColor, args=(1, 0, 0))
	id2 = master.add(name='strobe', pos=range(5), bufferType='mask', function=LEDController.strobe, args=(3,))
	master.exitThread(id2)
	
	# for i in range(300):
	# 	ws.set_pixel(i, 200, 0, 50)
	# 	ws.set_pixel(i+1, 100, 0, 50)
	# 	ws.set_pixel(i+2, 0, 0, 100)
		
	# 	ws.show()
	# 	sleep(0.05)

	while True:
		pass
		#master.finish = True
			
