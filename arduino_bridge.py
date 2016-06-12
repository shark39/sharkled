import sys
import glob
import time
import serial


def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result



class FastLED:

	def __init__(self, port):

		self.con = serial.Serial(port, 9600)

	def set_pixel(self, x, r, g, b):
		self.con.write(" ".join(map(str, [x, r, g, b])))


if __name__ == "__main__":

	try:
		leds = FastLED("/dev/tty.usbmodem1411")
		print("Found Port")
	except:
		print("Searching for ports")
		ports = serial_ports()
		for port in ports:
			answer = raw_input("Open " + port + "[y/n]")
			if answer == "y":
				print("Open Connection")
				leds = FastLED(port)
				break
	leds.set_pixel(9, 255, 0, 0)
	time.sleep(1.5)
	leds.set_pixel(10, 255, 255, 0)
	time.sleep(1)
	leds.set_pixel(11, 0, 255, 0)
	time.sleep(1)
	leds.set_pixel(12, 0, 255, 255)

	time.sleep(5)





