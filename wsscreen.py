
import colorsys
import Tkinter as tk 


def convrgb(r, g, b):
	return '#'+str('%6x' %((r << 16) + (g << 8) + b)).replace(' ', '0')


class Stripe:
	LEDS_COUNT = 150
	scale = 8

	leds = LEDS_COUNT*[convrgb(0, 0, 0)]
	brightness = 1

	def __init__(self):
				
		self.win = tk.Tk()
		self.win.title = "LED Stripe"

		self.canvas = tk.Canvas(self.win, bg="black", width=self.LEDS_COUNT*self.scale, height=self.scale)
		self.canvas.grid()

	def brightness(self, b=0.2):
	    self.brightness = b

	def get_brightness(self):
	    """Get the display brightness value
	    Returns a float between 0.0 and 1.0
	    """
	    return self.brightness

	def clear(self):
	    """Clear the buffer"""
	    for i in range(self.LEDS_COUNT):
	    	self.leds[i] = "#000000"

	def off(self):
	    """Clear the buffer and immediately update UnicornHat
	    Turns off all pixels."""
	    self.clear()
	    self.show()

	def set_pixel_hsv(self, index, h, s, v):
	    """Set a single pixel to a colour using HSV"""
	    r, g, b = [int(n*255) for n in colorsys.hsv_to_rgb(h, s, v)]
	    self.leds[index] = convrgb(r, g, b)
	    

	def set_pixel(self, x, r, g, b):
	    """Set a single pixel to RGB colour"""
	    self.leds[x] = convrgb(r, g, b) 

	def get_pixel(self, x):
	    """Get the RGB value of a single pixel"""
	    pixel = self.leds[x] 
	    return int(pixel[1:3], 16), int(pixel[3:5], 16), int(pixel[5:7], 16)


	def set_pixels(self, pixels):
	    pass

	def get_pixels(self):
	    """Get the RGB value of all pixels in a 7x7x3 2d array of tuples"""
	    return #[[get_pixel(x, y) for x in range(8)] for y in range(8)]


	def show(self):
	    """Update UnicornHat with the contents of the display buffer"""
	    self.canvas.delete('all')
	    for i, led in enumerate(self.leds):
	    	self.canvas.create_rectangle(i*self.scale, 0, (i+1)*self.scale, self.scale, fill=led)




if __name__ == '__main__':

	s = Stripe()
	for i in range(50, 100):
		s.set_pixel(i, 255, 255, 255)

	s.show()
	s.win.mainloop()
