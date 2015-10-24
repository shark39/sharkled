from time import sleep
from Queue import Queue
import threading
from threading import Thread
from time import sleep
from functools import partial
import sys

if sys.platform == 'linux2':
	## using raspberry
	RPI = True
	import unicornhat as ws
else:
	from wsscreen import Stripe 
	ws = Stripe() 
	RPI = False
	t = Thread(target=ws.win.mainloop, args=())
	#t.start()



class LEDMaster:

    def __init__(self):
        self.queue = Queue()

    def add(self, function, args=(), kwargs={}):
        t = Thread(target=self.run)
        t.daemon = True
        t.start()
        self.queue.put((function, args, kwargs))

    def execute(self, function, args, kwargs):
        partial(function, *args, **kwargs)()

    def run(self):
        while True:
            function, args, kwargs = self.queue.get()
            self.execute(function, args, kwargs)
            self.queue.task_done()

    def enumerateThreads(self):
    	return threading.enumerate()

    def enumerateControllers(self):
    	return []
            


class LEDController:

	def __init__(self, name, pos):
		self.pos = pos
		self.name = name
		self.leds = []


	def setColor(self, r, g, b):
		for p in self.pos:
			ws.set_pixel(p, r, g, b)
		ws.show()

	def strobe(self, frequency):
		
		leds = [ws.get_pixel(d) for d in self.pos]

		while True:
			ws.off()
			sleep(frequency/2)
			for p, d in zip(self.pos, leds):
				ws.set_pixel(p, *d)
			ws.show()	
			sleep(frequency/2)


	def pulsate(self, pos):
		for t in range(300): ## damits stoppt
			for i, p in enumerate(pos):
				## in hsv umrechnen
				h, s, v = colorsys.rgb_to_hsv(*ws.get_pixel(p))
				## mit sin(ID) multiplizieren
				new_h = (math.sin(i*2*math.pi/len(pos))+1)/2*h
				ws.set_pixel_hsv(p, new_h, s, v)
			ws.show()
			sleep(0.1)



	## zurueckumrechnen



	def off(self):
		ws.off()


