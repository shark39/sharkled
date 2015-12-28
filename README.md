# sharkled
Flask backend to control ws2812 led stripes via rasperry pi 

How to setup

Unicornhat lib for raspberry 
sudo python setup.py build
sudo python setup.py install



Code Overview

simplified code to get the main aspects of the code structure
```
| api.py
  ## contains all the endpoints
  ## for creating a new effect send a post request to /effect/...
  @app.route("/effect/<name>", methods=['POST', 'OPTIONS'])
  def effect(name):
  ## some processing
  lid = ledmaster.add(name=name, parameters=postdata) ## get the indentifier of the  effect
	return {id: lid, name: name, parameters: ledmaster.getControllerParameters(lid)} ## return id and all parameters
	
| LedControl.py
  ## handles all the logic
      class LEDMaster
        manage all effects and send the output to the led stripes
     |  Some methods defined here:
     |  
     |  add(self, name, parameters={})
     |      adds or updates the controller indentified by name
     |  
     |  writeBuffer(self)
     |      this function is running in an extra thread
     |      execute the effect function of the LEDControllers and set the pixels
     |  
     |  ----------------------------------------------------------------------
     |  Static methods defined here:
     |  
     |  getDefaultParameters(effect)
     |  
     |  getEffects()
      
      class LEDEffect(LEDController)
        contains all the effects as methods with default values
       |  Some methods defined here:
       |  
       |  color(self, ts, pos, color=[1, 1, 1, 1], **kwargs)
       |      Description: set a solid color
       |      return len(pos) * [color]
       |
       |  pulsate(self, ts, pos, interval=1000, wavelength=100, color=[1, 1, 1, 1], background=[0, 0, 0, 0], **kwargs)
       |      Description: generates a pulsating light
       |  
```


