import unicornhat as ws
from time import sleep
import random

sleep(1)


ws.brightness(0.1)


while True:
    h = random.randint(10, 50)
    r, g, b = random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)
    for i in range(h):
        ws.set_pixel(i, r, g, b)
        ws.show()
        sleep(0.02)

    for i in range(h, 0, -1):
        ws.set_pixel(i, 0, 0, 0)
        ws.show()
        sleep(0.02)
        
