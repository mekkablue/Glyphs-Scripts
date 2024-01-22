
import math
from typing import Any
from AppKit import NSAffineTransform, NSUserDefaults
from GlyphsApp import Glyphs


if Glyphs.versionNumber >= 3:
	from GlyphsApp import GSUppercase, GSLowercase, GSSmallcaps, GSMinor, GSNoCase
	caseDict = {
		"Lower": GSLowercase,
		"lower": GSLowercase,
		"Lowercase": GSLowercase,
		"lowercase": GSLowercase,
		"Minor": GSMinor,
		"minor": GSMinor,
		"NoCase": GSNoCase,
		"nocase": GSNoCase,
		"SC": GSSmallcaps,
		"sc": GSSmallcaps,
		"Small": GSSmallcaps,
		"small": GSSmallcaps,
		"Smallcaps": GSSmallcaps,
		"smallcaps": GSSmallcaps,
		"Upper": GSUppercase,
		"upper": GSUppercase,
		"Uppercase": GSUppercase,
		"uppercase": GSUppercase,
	}
else:
	caseDict = {}


def match(first, second):
	# https://www.geeksforgeeks.org/wildcard-character-matching/

	# If we reach at the end of both strings, we are done
	if len(first) == 0 and len(second) == 0:
		return True

	# Make sure that the characters after '*' are present
	# in second string. This function assumes that the first
	# string will not contain two consecutive '*'
	if len(first) > 1 and first[0] == '*' and len(second) == 0:
		return False

	# If the first string contains '?', or current characters
	# of both strings match
	if (len(first) > 1 and first[0] == '?') or (len(first) != 0 and len(second) != 0 and first[0] == second[0]):
		return match(first[1:], second[1:])

	# If there is *, then there are two possibilities
	# a) We consider current character of second string
	# b) We ignore current character of second string.
	if len(first) != 0 and first[0] == '*':
		return match(first[1:], second) or match(first, second[1:])

	return False


def camelCaseSplit(string: str) -> str:
	words = [[string[0]]]
	for c in string[1:]:
		if words[-1][-1].islower() and c.isupper():
			words.append(list(c))
		else:
			words[-1].append(c)
	return [''.join(word) for word in words]


def transform(shiftX=0.0, shiftY=0.0, rotate=0.0, skew=0.0, scale=1.0) -> NSAffineTransform:
	"""
	Returns an NSAffineTransform object for transforming layers.
	Apply an NSAffineTransform t object like this:
		Layer.transform_checkForSelection_doComponents_(t,False,True)
	Access its transformation matrix like this:
		tMatrix = t.transformStruct()  # returns the 6-float tuple
	Apply the matrix tuple like this:
		Layer.applyTransform(tMatrix)
		Component.applyTransform(tMatrix)
		Path.applyTransform(tMatrix)
	Chain multiple NSAffineTransform objects t1, t2 like this:
		t1.appendTransform_(t2)
	"""
	myTransform = NSAffineTransform.transform()
	if rotate:
		myTransform.rotateByDegrees_(rotate)
	if scale != 1.0:
		myTransform.scaleBy_(scale)
	if not (shiftX == 0.0 and shiftY == 0.0):
		myTransform.translateXBy_yBy_(shiftX, shiftY)
	if skew:
		myTransform.shearBy_(math.tan(math.radians(skew)))
	return myTransform


class mekkaObject:

	def domain(self, prefName: str) -> str:
		prefName = prefName.strip().strip(".")
		return "com.mekkablue." + self.__class__.__name__ + "." + prefName.strip()

	def pref(self, prefName: str) -> Any:
		prefDomain = self.domain(prefName)
		# print(prefName, "-> getting domain", prefDomain, "<<<")  # DEBUG
		prefValue = Glyphs.defaults[prefDomain]
		if prefValue:
			return prefValue
		return self.prefDict[prefName]

	def prefBool(self, prefName: str) -> bool:
		prefDomain = self.domain(prefName)
		return NSUserDefaults.standardUserDefaults().boolForKey_(prefDomain)

	def prefInt(self, prefName: str) -> int:
		prefDomain = self.domain(prefName)
		return NSUserDefaults.standardUserDefaults().integerForKey_(prefDomain)

	def prefFloat(self, prefName: str) -> float:
		prefDomain = self.domain(prefName)
		return NSUserDefaults.standardUserDefaults().doubleForKey_(prefDomain)

	def setPref(self, prefName: str, value: Any):
		prefDomain = self.domain(prefName)
		Glyphs.defaults[prefDomain] = value

	def uiElement(self, prefName: str) -> Any:
		particles = prefName.split(".")
		latestObject = self.w
		for particle in particles:
			latestObject = getattr(latestObject, particle)
		return latestObject

	def LoadPreferences(self):
		try:
			for prefName in self.prefDict.keys():
				# register defaults:
				Glyphs.registerDefault(self.domain(prefName), self.prefDict[prefName])
				# load previously written prefs:
				self.uiElement(prefName).set(self.pref(prefName))
			if hasattr(self, "updateGUI"):
				self.updateGUI()
		except:
			import traceback
			print(traceback.format_exc())
			print(f"⚠️ ‘{self.__class__.__name__}’ could not load preferences. Will resort to defaults.")

	def SavePreferences(self, sender=None):
		try:
			# write current settings into prefs:
			for prefName in self.prefDict.keys():
				Glyphs.defaults[self.domain(prefName)] = getattr(self.w, prefName).get()
		except:
			import traceback
			print(traceback.format_exc())
			print(f"⚠️ ‘{self.__class__.__name__}’ could not write preferences.")
