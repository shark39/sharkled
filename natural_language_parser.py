import collections
import jellyfish
from LedControl import LEDMaster
from constants import *
from colornames import COLORS

class NLP:
	def __init__(self):
		## find areas
		self.threshold = 0.75
		self.parameters_indicators = [u"with", u"parameters"]
		self.gap_words = [u"and"]
		self.effect_choices = [e['name'] for e in LEDMaster.getEffects()]
		self.inpterpretation = []

	def process(self, text):
		'''text is plaintext of nlp input'''
		self.inpterpretation = []
		words = text.split()
		areas = self.findAreas(words)
		p_i = self.getParameterIndicatorIndex(words)
		if p_i > 0:
			effect = self.findEffectName(words[:p_i])
			parameters = self.findParameters(words[p_i+1:], effect)
		else:
			effect = self.findEffectName(words)
			parameters = self.findParameters(words, effect)

		inpterpretation = collections.namedtuple("inpterpretation",  "effect areas parameters")
		inpterpretation.effect = effect
		inpterpretation.areas = areas
		inpterpretation.parameters = parameters
		return inpterpretation

	def findAreas(self, words):
		'''find every word that could indicate the area.
		TODO: handle numbers, handle aliases, choose lowest granularity'''
		areas = []
		for i, word in enumerate(words): ## TODO detect stuff like Balken1, Wand2
			for a in AREAS:
				if a[-1] in '1234': #skip Balken1, 2 and so on 
					continue ## TODO detect if number is attached
				if jellyfish.jaro_distance(unicode(a), unicode(word)) > self.threshold and a not in areas:
					areas.append(a)
		return areas 

	def getParameterIndicatorIndex(self, words):
		'''return index of word which could mostly indicate the beginning of parameter inputs'''
		best_match = 0
		best_index = 0
		for i, word in enumerate(words):
			for pi in self.parameters_indicators:
				match = jellyfish.jaro_distance(pi, unicode(word))
				if match > self.threshold and match > best_match:
					best_match = match
					best_index = i
					if match == 1:
						return i ## shortcut, no need to search for more
		return best_index



	def findEffectName(self, words):
		'''search only in words before buzzword paramerers'''
		## find effect name
		## word with highest match and before keyword parameters
		choices = self.effect_choices
		best_match_effect = collections.namedtuple('Match', 'effect chance')
		best_match_effect.chance = 0
		for effect in choices:
			for i, word in enumerate(words):
				match = jellyfish.jaro_distance(unicode(effect), unicode(word)) 
				if match > best_match_effect.chance and match > self.threshold:
					best_match_effect.chance = match
					best_match_effect.effect = effect
			
		return best_match_effect.effect


	def findParameters(self, words, effectname):
		''' only check words after a parameter indicator'''
		parameters = LEDMaster.getDefaultParameters(effectname) ## always load default 
		for i, word in enumerate(words):
			for j, p in enumerate(parameters.keys()):
					match = jellyfish.jaro_distance(unicode(p), unicode(word)) 
					if match > self.threshold:
						value = self.understandParameterValue(p, parameters[p], words[i+1:])
						parameters[p] = value
		return parameters

						
	def understandParameterValue(self, parametername, defaultvalue, words):
		'''words is a list with all words after the parametername'''
		##convert value after keyword to correct type
		correct_type = type(defaultvalue)
		if correct_type == list and len(defaultvalue) == 4: ## assume that we have a color here
			value = self.interpretAsColor(words)
		else:	
			try: 
				value = correct_type(words[0])
			except IndexError:
				pass ## last index
			except:
				print "exception"					
				print "Failed to decode ", words[0]
		
		if value:
			return value
		return defaultvalue
					

	def interpretAsColor(self, words):
		'''tries to map to first couple of words to a color'''
		best_match_color = collections.namedtuple('Match', 'index chance')
		best_match_color.chance = 0
		for i, word in enumerate(words):
			for j, color in enumerate(COLORS):
				matches = []
				for k, c in enumerate(color['name'].split(), start=0):
					try:
						m = jellyfish.jaro_distance(unicode(c), unicode(words[i+k])) 
					except IndexError:
						break ## end of words
					else:
						matches.append(m)
				match = sum(matches)/len(matches)
				if match > self.threshold and match > best_match_color.chance:
					best_match_color.chance = match
					best_match_color.index = j
					if best_match_color.chance > 0:
						rgb = map(lambda x: x/255.0, list(eval(COLORS[best_match_color.index]['rgb']))) + [1]
						return rgb
		return None

	def interpretAsPercent(self, words):
		pass
				


			
						

	
if __name__ == "__main__":
	## TODO and wird als wand interpretiert
	nlp = NLP()
	messages = ["new effect chaser with interval 1000 color jungle green", "rainbow for all", "chase with interval 3000 count 10"]
	print "Test NLP"
	for m in messages:
		print m
		r1 =  nlp.process(m)
		print "Effect:", r1.effect
		print "Areas:", r1.areas
		print "Parameters:", r1.parameters
