from time import sleep
import threading
from threading import Thread
from time import sleep
from functools import partial
import sys


if sys.platform in ['linux2', 'linux']:
	## using raspberry
	RPI = True
	import unicornhat as ws
else:
	#from wsscreen import Stripe 
	#ws = Stripe() 
	RPI = False
	#t = Thread(target=ws.win.mainloop, args=())
	#t.start()



class LEDMaster:

    def __init__(self):
        
        self.controllers = []

    def add(self, instance, function, args=(), kwargs={}):

      t = Thread(target=function, args=args)
      t.start()
      self.controllers.append((instance, t))


    def enumerateControllers(self):
    	#self.controllers = filter(lambda x: not x[0].finish, self.controllers)
    	#print[c.name for c, x in self.controllers]
    	return self.controllers



    def enumerateThreads(self):
    	return threading.enumerate()

    def enumerateControllers(self):
    	return []
            


class LEDController:

	def __init__(self, name, pos):
		self.pos = pos
		self.name = name
		self.leds = []
		self.finish = False


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
			if self.finish:
				return


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


	def finishThread(self):
		self.finish = True



	## zurueckumrechnen



	def off(self):
		ws.off()


if __name__ == '__main__':



	master = LEDMaster()
	c = LEDController('1', range(10))
	t1 = Thread(target=c.setColor, args=(255, 0, 0))
	t1.start()
	print("Number of Threads: ", len(master.enumerateThreads()))
		
	c = LEDController('1', range(10, 20))
	t3 = Thread(target=c.setColor, args=(255, 255, 0))
	t3.start()
	
	#print "Number of Threads: ", len(master.enumerateThreads())


	c1 = LEDController('1', range(0, 20))
	t2 = Thread(target=c1.strobe, args=(3,))
	t2.start()
	
	#print "Number of Threads: ", len(master.enumerateThreads())
	

	c = LEDController('1', range(10, 30))
	c.setColor(255, 255, 255)
	#print "Number of Threads: ", len(master.enumerateThreads())


	c = LEDController('1', range(0, 30))
	t2 = Thread(target=c.strobe, args=(2,))
	t2.start()

	c1.finishThread()
	
		
