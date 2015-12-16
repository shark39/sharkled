
import time

class Timer:

	def __init__(self):
		self.startedAt = time.time()

	def start(self):
		self.startedAt = time.time()

	def wait(self, sec=0, millisec=0):
		duration = sec+1.0*millisec/1000
		time.sleep(max(0, self.startedAt+duration-time.time()))