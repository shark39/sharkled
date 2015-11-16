from time import sleep
import threading
from threading import Thread
from time import sleep
from  datetime import datetime
from functools import partial
import sys
from logging import FileHandler, Formatter, getLogger, DEBUG

if sys.platform in ['linux2', 'linux']:
	## using raspberry
	RPI = True
	import unicornhat as ws
else:
	from wsscreen import Stripe 
	ws = Stripe() 
	RPI = False
	t = Thread(target=ws.win.mainloop, args=())
	t.start()



class LEDMaster:

	def __init__(self):
		
		self.controllers = []
		self.id = 0
		self.mask = ws.LED_COUNT*[1]
		self.color = ws.LED_COUNT*[(0,0,0)]
		self.finish = False
		self.bufferThread = Thread(target=self.writeBuffer)
		self.bufferThread.start()
		## start buffer writing thread


	def add(self, name, pos, bufferType, function, args=(), kwargs={}):

		self.id += 1
		t = Thread(target=function, args=(LEDController(name, pos, bufferType, self.setLeds), ) + args)
		t.start()
		self.controllers.append((t, self.id))


	def enumerateControllers(self):
		self.controllers = filter(lambda x: not x[0].finish, self.controllers)
		#print[c.name for c, x in self.controllers]
		return self.controllers

	def finishController(self, name=None, id=None, mode=None):
		droplist = []
		for c, t, i in self.controllers:
			if not c.finish and name and name==c.name:
				droplist.append(c)
		for c in droplist:
			c.finish = True


	def enumerateControllersEffect(self):
		pass


	def enumerateThreads(self):
		return threading.enumerate()

	def enumerateControllers(self):
		return []

	def getLeds(self):
		out = []
		for i in range(ws.LED_COUNT):
			out.append(ws.get_pixel(i))
		return out

	def setLeds(self, controller):
		print controller
		for i, pos in enumerate(controller.pos):
			if controller.bufferType == 'mask':
				self.mask[pos] = controller.mask[i]
			if controller.bufferType == 'color':
				self.color[pos] = controller.color[i]
				#print 'set led: %i to %s' %(pos, str(controller.color[i]))
		#self.finish = True
		#self.writeBuffer()

	def writeBuffer(self):
		while True:
			for i, (m, c) in enumerate(zip(self.mask, self.color)):
				ws.set_pixel(i, int(255*c[0]*m), int(255*c[1]*m), int(255*c[2]*m))
				#print "write pixel %i: %i %i %i" %(i, 255*c[0]*m, 255*c[1]*m, 255*c[2]*m) 
				#if sum(c) > 0:
				#	print "write buffer", i, 255*c[0]*m, 255*c[1]*m, 255*c[2]*m
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

	def __repr__(self):
		return "LEDController " + self.name + '(' + str(len(self.pos)) + 'leds)'

	def __str__(self):
		return "LEDController " + self.name + '(' + str(len(self.pos)) + 'leds)'

	def set(self):
		self.setfunc(self)



	def setColor(self, r, g, b):
		self.color = map(lambda x: (r, g, b), self.color) #len(self.pos) * [(r, g, b)]
		self.set()
		self.finish = True
		

	def strobe(self, frequency):
		
		while True:
			self.mask = map(lambda x: 0, self.mask)
			self.set()
			sleep(frequency/2)
			self.mask = map(lambda x: 1, self.mask)	
			self.set()
			sleep(frequency/2)
			if self.finish:
				return


	def pulsate(self):
		pos = range(1)
		for t in range(300): ## damits stoppt
			for i, p in enumerate(pos):
				## in hsv umrechnen
				h, s, v = colorsys.rgb_to_hsv(*ws.get_pixel(p))
				## mit sin(ID) multiplizieren
				new_h = (math.sin(i*2*math.pi/len(pos))+1)/2*h
				ws.set_pixel_hsv(p, new_h, s, v)
			ws.show()
			sleep(0.1)


	def finishThread(self):
		self.finish = True



	## zurueckumrechnen



	def off(self):
		ws.off()


if __name__ == '__main__':


	master = LEDMaster()
	master.add(name='color', pos=range(10), bufferType='color', function=LEDController.setColor, args=(1, 0, 0))
	
	# for i in range(300):
	# 	ws.set_pixel(i, 200, 0, 50)
	# 	ws.set_pixel(i+1, 100, 0, 50)
	# 	ws.set_pixel(i+2, 0, 0, 100)
		
	# 	ws.show()
	# 	sleep(0.05)

	while True:
		pass
		#master.finish = True
			
