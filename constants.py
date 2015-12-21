from LedControl import LEDController

AREAS = {
	"Wand" : range(0, 32)+range(297, 267, -1)+range(330, 298, -1), 
	"Balken1": range(32, 150),  
	"Balken2": range(267, 150, -1),
	"Balken3": range(330, 448)}
LEDS_COUNT = 600

