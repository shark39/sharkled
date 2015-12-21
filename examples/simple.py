#!/usr/bin/env python

import unicornhat as UH
import time
while True:
	for y in range(600):
	    UH.set_pixel(y,255,255,255)
	UH.show()
	for y in range(600):
	    UH.set_pixel(y,0,0,0)
	UH.show()
