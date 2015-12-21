from neopixel import *
import atexit
import colorsys
# LED strip configuration:
LED_COUNT      = 450      # Number of LED pixels.
LED_PIN        = 18      # GPIO pin connected to the pixels (must support PWM!).
LED_FREQ_HZ    = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA        = 5       # DMA channel to use for generating signal (try 5)
LED_BRIGHTNESS = 255     # Set to 0 for darkest and 255 for brightest
LED_INVERT     = False   # True to invert the signal (when using NPN transistor level shift)

ws2812 = Adafruit_NeoPixel(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS)
ws2812.begin()

"""
Store the rotation of UnicornHat, defaults to
0 which places 0,0 on the top left with the B+
HDMI port facing downwards
"""
_rotation = 0




def _clean_shutdown():
    """Registered at exit to ensure ws2812 cleans up after itself
    and all pixels are turned off.
    """
    off()



def brightness(b=0.2):
    """Set the display brightness between 0.0 and 1.0

    0.2 is highly recommended, UnicornHat can get painfully bright!"""

    if b > 1 or b < 0:
        raise ValueError('Brightness must be between 0.0 and 1.0')

    ws2812.setBrightness(int(b*255.0))


def get_brightness():
    """Get the display brightness value

    Returns a float between 0.0 and 1.0
    """
    return 0#ws2812.getBrightness()


def clear():
    """Clear the buffer"""
    for x in range(LED_COUNT):
        ws2812.setPixelColorRGB(x, 0, 0, 0)


def off():
    """Clear the buffer and immediately update UnicornHat

    Turns off all pixels."""
    clear()
    show()


def set_pixel_hsv(index, y, h, s, v):
    """Set a single pixel to a colour using HSV"""
    r, g, b = [int(n*255) for n in colorsys.hsv_to_rgb(h, s, v)]
    ws2812.setPixelColorRGB(index, r, g, b)


def set_pixel(x, r, g, b):
    """Set a single pixel to RGB colour"""
    ws2812.setPixelColorRGB(x, r, g, b)


def get_pixel(index):
    """Get the RGB value of a single pixel"""
    pixel = ws2812.getPixelColorRGB(index)
    return int(pixel.r), int(pixel.g), int(pixel.b)


def set_pixels(pixels):
    for x in range(LED_COUNT):
        r, g, b = pixels[x]
        set_pixel(x, r, g, b)


def get_pixels():
    """Get the RGB value of all pixels in a 7x7x3 2d array of tuples"""
    return [get_pixel(x) for x in range(LED_COUNT)]


def show():
    """Update UnicornHat with the contents of the display buffer"""
    ws2812.show()


atexit.register(_clean_shutdown)
