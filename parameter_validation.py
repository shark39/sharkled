import collections
from constants import *
from colornames import COLORS
from LedControl import LEDMaster
class Validator:
	''' '''

	@staticmethod
	def areas(post):
		'''handles the following:
		- if no area, it adds all
		- if area has wrong format it try to convert
		- if area not valid it ignores the area
		- if area is empty, replace with all
		- if dublicates in area, remove the latest
		- correct uppercase and lowercase letters
		'''
		validation = collections.namedtuple('validation', 'post warnings')
		validation.warnings = []
		validation.post = post
		# if no area, it adds all
		if not validation.post.has_key("areas"):
			validation.post["areas"] = ['All']
			validation.warnings.append("Parameter 'areas' was missing, replaced with All")
			return validation
		# if area is empty, replace with all
		if validation.post["areas"] == []:
			validation.post["areas"] = ['All']
			validation.warnings.append("Parameter 'areas' was empty list, added All")
			return validation
		#if area has wrong format it try to convert
		if type(validation.post["areas"]) != list:
			if type(validation.post["areas"]) in [str, unicode]:
				validation.post["areas"] = str(validation.post["areas"])
				validation.post["areas"] = [validation.post["areas"]]
				validation.warnings.append("Parameter area has the wrong format, converted from string to list")
			else:
				validation.warnings.append("[ERROR] Parameter area has the wrong format")
				return validation
		# if area not valid it ignores the area
		i = 0
		while i < len(validation.post["areas"]):
			a = validation.post["areas"][i]
			if a.capitalize() not in AREAS:
				validation.warnings.append("Cannot find area %s, removed" %a)
				validation.post["areas"].pop(i)
			else:
				validation.post["areas"][i] = a.capitalize() #correct uppercase and lowercase letters
				i += 1
		# if dublicates in area, remove the latest
		if len(validation.post["areas"]) > len(set(validation.post["areas"])):
			validation.warnings.append("dublicates in areas, remove the latest each")
			validation.post["areas"] = list(set(validation.post["areas"]))
		return validation


	@staticmethod
	def z(post):
		'''if z not in post, set z=0'''
		warnings = []
		if not post.has_key("z"):
			warnings.append("Missing parameter z, added z=0")
			post["z"] = 0

		validation = collections.namedtuple('validation', 'post warnings')
		validation.warnings = warnings
		validation.post = post
		return validation

	@staticmethod
	def color(post, keywords=['color', 'background']):
		'''convert from rgb 0..255
		convert from rgb 0..1
		convert from rgb hex
		convert from colorname
		convert from rgb to rgba
		'''
		warnings = []
		for key in keywords:
			if post.get(key):
				if type(post.get(key)) == list and len(post[key]) >= 3:
					try:
						if all(map(lambda c: 0 <= float(c) <= 1, post[key])):
							pass ## everything as expected
						elif all(map(lambda c: 0 <= int(c) <= 255, post[key])): # if 0..255
							post[key] = [float(c)/255 for c in post[key]]
					except:
						warnings.append("can not decode color parameter %s (tried as array)" %str(post[key]))
						del post[key]
				elif type(post.get(key)) in [str, unicode]:
					post[key] = str(post[key])
					if post[key].find('#') == 0:
						try: 
							post[key] = map(lambda x: int(x, 16)/255.0, [post[key][1:3], post[key][3:5], post[key][5:7]]) + [1]
						except:
							warnings.append("can not decode color parameter %s (tried as hex)" %str(post[key]))
							del post[key]
					else: ## interpret as color
						success = False
						for data in COLORS: ## find in color names
							if data['name'].lower() == post[key].strip().lower():
								post[key] = map(lambda x: x/255.0, list(eval(data['rgb']))) + [1]
								success = True
								break
						if not success:
							warnings.append("Cannot find the color name %s" %post[key])
							del post[key]

				else:
					warnings.append("can not decode color parameter %s" %str(post[key]))
					del post[key]

				if type(post.get(key)) == list and len(post[key]) == 3:
					warnings.append("missing alpha value in color")
					post[key].append(1)
				
		validation = collections.namedtuple('validation', 'post warnings')
		validation.warnings = warnings
		validation.post = post
		return validation

	@staticmethod
	def colorlist(post, keywords=["colors"]):
		'''apply the color validation for all items in the list'''
		warnings = []
		for key in keywords:
			if post.get(key) and type(post[key]) == list:
				new_value = []
				for i, c in enumerate(post[key]):
					v = Validator.color({"color": c})
					warnings += v.warnings
					if v.post.get("color"):
						new_value.append(v.post["color"])
				post[key] = new_value
			else:
				warnings.append("%s must be a list" %key)

		validation = collections.namedtuple('validation', 'post warnings')
		validation.warnings = warnings
		validation.post = post
		return validation

	@staticmethod
	def fadespeed(post):
		'''todo warning if speed is to high'''
		warnings = []
		if post.get("fadespeed"):
			try:
				f = float(post['fadespeed'])
			except:
				warnings.append("wrong format for fadespeed")
			else:
				if f <= 1 and post.get("interval"):
					f = f * float(post["interval"]) ## TODO make sure that interval is validated
					warnings.append("interpreted fadespeed as a relative value, converted to absolute value depending on interval")
				post["fadespeed"] = f 

		validation = collections.namedtuple('validation', 'post warnings')
		validation.warnings = warnings
		validation.post = post
		return validation




	@staticmethod
	def addMissing(name, post):
		warnings = []
		parameters = LEDMaster.getDefaultParameters(name)
		for p,v in parameters.items():
			if p not in post:
				post[p] = v 
				warnings.append("Parameter %s was missing, set to default value" %p)

		validation = collections.namedtuple('validation', 'post warnings')
		validation.warnings = warnings
		validation.post = post
		return validation

	@staticmethod
	def findObsolete(name, post, ignore=['areas', 'z', 'mergeType']):
		'''will not remove obsolete parameters, but adds a warning to the list'''
		warnings = []
		parameters = LEDMaster.getDefaultParameters(name)
		for p, v in post.items():
			if p not in parameters and p not in ignore:
				warnings.append("Parameter %s is obsolete" %p)
		validation = collections.namedtuple('validation', 'post warnings')
		validation.warnings = warnings
		validation.post = post
		return validation




if __name__ == "__main__":

	print "Test Validator.area"
	print "Test wring type string"
	v1 = Validator.areas({"areas" : "all"})
	assert v1.post["areas"] == ["All"]
	print "Test no areas"
	v2 = Validator.areas({"areasdasd" :[]})
	assert v2.post["areas"] == ["All"]
	print "Test wrong area and dublicate"
	v3 = Validator.areas({"areas" :["Balken1", "Balken5", "Balken1"]})
	assert v3.post["areas"] == ["Balken1"]
	print "Test unicode wand"
	v3 = Validator.areas({"areas" :"wand"})
	assert v3.post["areas"] == ["Wand"]

	print "Test Validator.color"
	print "Test hex"
	v1 = Validator.color({"color" : "#ffffff"})
	assert v1.post["color"] == [1, 1, 1, 1]
	print "Test name"
	v = Validator.color({"color" : "Sunset orange"})
	assert v.post["color"] == [253.0/255, 94.0/255, 83.0/255, 1]

	print "Test name unicode"
	v = Validator.color({"color" : u"sunset orange"})
	assert v.post["color"] == [253.0/255, 94.0/255, 83.0/255, 1]

	print "Test normal len 3"
	v = Validator.color({"color" : [0.5, 1, 0]})
	assert v.post["color"] == [0.5, 1, 0, 1]

	print "Test 0..255"
	v = Validator.color({"color" : [255, 255, 255, 0]})
	assert v.post["color"] == [1, 1, 1, 0]

	print "Test short list"
	v = Validator.color({"color" : [255, 25]})
	assert v.post == {}
	assert len(v.warnings) == 1

	print "Test bullshit name"
	v = Validator.color({"color" : "random cyan"})
	assert v.post == {}
	assert len(v.warnings) == 1

	print "Test Validator.colorlist"
	print "Test mixed array"
	v = Validator.colorlist({"colors" : ["random cyan", [1,1,1,1]]})
	assert v.post["colors"] == [[1,1,1,1]]
	assert len(v.warnings) == 1
	

	print "Test Validator.addMissing"
	print "Test for color"
	v = Validator.addMissing("color", {"z" : 0})
	assert v.post["color"] == [1,1,1,1]
	assert len(v.warnings) == 1

	print "Test Validator.findObsolete"
	print "Test for color"
	v = Validator.findObsolete("color", {"z" : 0, "background": ''})
	assert v.post == {"z" : 0, "background": ''}
	assert len(v.warnings) == 1


	print "Test Validator.fadespeed"
	print "Test for normal value"
	v = Validator.fadespeed({"fadespeed": '200', "interval" : 1000})
	assert v.post["fadespeed"] == 200
	assert len(v.warnings) == 0

	print "Test for normal value"
	v = Validator.fadespeed({"fadespeed": 0.5, "interval" : 1000})
	assert v.post["fadespeed"] == 500
	assert len(v.warnings) == 1

	print "Test for 100%==1"
	v = Validator.fadespeed({"fadespeed": 1, "interval" : 1000})
	assert v.post["fadespeed"] == 1000
	assert len(v.warnings) == 1

	print "All Tests finished"





