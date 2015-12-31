
import collections
from constants import *

class Validator:
	''' '''

	@staticmethod
	def areas(post):
		'''handles the following:
		- if no area, it adds all
		- if area has wrong format it try to convert
		- if area not valid it ignores the area
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
		#if area has wrong format it try to convert
		if type(validation.post["areas"]) != list:
			if type(validation.post["areas"]) == str:
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
		warnings = []
		if not post.has_key("z"):
			warnings.append("Missing parameter z, added z=0")
			post["z"] = 0

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


	print "All Tests finished"





