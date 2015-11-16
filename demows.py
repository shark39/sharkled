import unicornhat as ws
from time import sleep





if __name__ == '__main__':

	for i in range(300):
		ws.set_pixel(i, 200, 0, 50)
		ws.set_pixel(i+1, 100, 0, 50)
		ws.set_pixel(i+2, 0, 0, 100)
		
		ws.show()
		sleep(0.05)

	while True:
		pass