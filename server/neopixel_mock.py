# Adafruit NeoPixel library port to the rpi_ws281x library.



def Color(red, green, blue, white = 0):
	"""Convert the provided red, green, blue color to a 24-bit color value.
	Each color component should be a value 0-255 where 0 is the lowest intensity
	and 255 is the highest intensity.
	"""
	return (white << 24) | (red << 16)| (green << 8) | blue


class _LED_Data(object):
	"""Wrapper class which makes a SWIG LED color data array look and feel like
	a Python list of integers.
	"""
	def __init__(self, channel, size):
		pass

	def __getitem__(self, pos):
		"""Return the 24-bit RGB color value at the provided position or slice
		of positions.
		"""
		# Handle if a slice of positions are passed in by grabbing all the values
		# and returning them in a list.
		return None

	def __setitem__(self, pos, value):
		"""Set the 24-bit RGB color value at the provided position or slice of
		positions.
		"""
		# Handle if a slice of positions are passed in by setting the appropriate
		# LED data values to the provided values.
		return None


class Adafruit_NeoPixel(object):
	def __init__(self, num, pin, freq_hz=800000, dma=5, invert=False,
			brightness=255, channel=0, strip_type=None):
		"""Class to represent a NeoPixel/WS281x LED display.  Num should be the
		number of pixels in the display, and pin should be the GPIO pin connected
		to the display signal line (must be a PWM pin like 18!).  Optional
		parameters are freq, the frequency of the display signal in hertz (default
		800khz), dma, the DMA channel to use (default 5), invert, a boolean
		specifying if the signal line should be inverted (default False), and
		channel, the PWM channel to use (defaults to 0).
		"""
		# Create ws2811_t structure and fill in parameters.
		pass

	def __del__(self):
		# Required because Python will complain about memory leaks
		# However there's no guarantee that "ws" will even be set
		# when the __del__ method for this class is reached.
		pass

	def _cleanup(self):
		# Clean up memory used by the library when not needed anymore.
		pass

	def begin(self):
		"""Initialize library, must be called once before other functions are
		called.
		"""
		pass

	def show(self):
		"""Update the display with the data from the LED buffer."""
		pass

	def setPixelColor(self, n, color):
		"""Set LED at position n to the provided 24-bit color value (in RGB order).
		"""
		pass

	def setPixelColorRGB(self, n, red, green, blue, white = 0):
		"""Set LED at position n to the provided red, green, and blue color.
		Each color component should be a value from 0 to 255 (where 0 is the
		lowest intensity and 255 is the highest intensity).
		"""
		pass

	def setBrightness(self, brightness):
		"""Scale each LED in the buffer by the provided brightness.  A brightness
		of 0 is the darkest and 255 is the brightest.
		"""
		pass

	def getPixels(self):
		"""Return an object which allows access to the LED display data as if
		it were a sequence of 24-bit RGB values.
		"""
		return

	def numPixels(self):
		"""Return the number of pixels in the display."""
		return ws.ws2811_channel_t_count_get(self._channel)

	def getPixelColor(self, n):
		"""Get the 24-bit RGB color value for the LED at position n."""
		return
