
from typing import Any
from AppKit import NSUserDefaults, NSFont, NSImage, NSImageLeading, NSPasteboard, NSStringPboardType, NSLineBreakByClipping
from GlyphsApp import Glyphs, GSFeature, GSClass
from vanilla import Button

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


def getClipboard(verbose=False):
	"""
	Gets the plain text contents of the clipboard.
	Returns the string if successful, or None if no text is available.
	"""
	try:
		myClipboard = NSPasteboard.generalPasteboard()
		content = myClipboard.stringForType_(NSStringPboardType)
		return content
	except Exception as e:
		print("Error: could read clipboard contents as plain text.")
		print(e)
		return None


def setClipboard(myText, verbose=False):
	"""
	Sets the contents of the clipboard to myText.
	Returns True if successful, False if unsuccessful.
	"""
	try:
		myClipboard = NSPasteboard.generalPasteboard()
		myClipboard.declareTypes_owner_([NSStringPboardType], None)
		myClipboard.setString_forType_(myText, NSStringPboardType)
		return True
	except Exception as e:
		if verbose:
			print("Error: could set clipboard contents.")
			print(e)
		return False


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
	if (len(first) != 0 and len(second) != 0 and first[0] == '?') or (len(first) != 0 and len(second) != 0 and first[0] == second[0]):
		return match(first[1:], second[1:])

	# If there is *, then there are two possibilities
	# a) We consider current character of second string
	# b) We ignore current character of second string.
	if len(first) != 0 and first[0] == '*':
		return match(first[1:], second) or match(first, second[1:])

	return False


def camelCaseSplit(string: str) -> list[str]:
	words = [[string[0]]]
	for c in string[1:]:
		if words[-1][-1].islower() and c.isupper():
			words.append(list(c))
		else:
			words[-1].append(c)
	return [''.join(word) for word in words]



def reportTimeInNaturalLanguage(seconds):
	if seconds > 60.0:
		timereport = "%i:%02i minutes" % (seconds // 60, seconds % 60)
	elif seconds < 1.0:
		timereport = "%.2f seconds" % seconds
	elif seconds < 20.0:
		timereport = "%.1f seconds" % seconds
	else:
		timereport = "%i seconds" % seconds
	return timereport


def reportFontName(font) -> str:
	"""
	Returns a display name for a font for use in log output.
	If the font file is saved, returns '<filename>\n📄 <path>'.
	If not saved, returns '<familyName>\n⚠️ The font file has not been saved yet.'
	"""
	filePath = font.filepath
	if filePath:
		return f"{filePath.lastPathComponent()}\n📄 {filePath}"
	return f"{font.familyName}\n⚠️ The font file has not been saved yet."


def getLegibleFont(size=None):
	if size is None:
		size = NSFont.systemFontSize()
	try:
		legibleFont = NSFont.legibleFontOfSize_(size)
	except:
		legibleFont = NSFont.legibileFontOfSize_(size)  # Glyphs 3.1 compatibilty
	return legibleFont


def UpdateButton(posSize, callback, title=""):
	button = Button(posSize, title, callback=callback)
	button.getNSButton().setImage_(NSImage.imageNamed_("NSRefreshTemplate"))
	if len(title) > 0:
		button.getNSButton().setImagePosition_(NSImageLeading)
	button.getNSButton().setBordered_(False)
	return button


def updatedCode(oldCode, beginSig, endSig, newCode):
	"""Replaces text in oldCode with newCode, but only between beginSig and endSig."""
	beginOffset = oldCode.find(beginSig)
	endOffset = oldCode.find(endSig) + len(endSig)
	newCode = oldCode[:beginOffset] + beginSig + newCode + "\n" + endSig + oldCode[endOffset:]
	return newCode


def createOTFeature(featureName="calt", featureCode="# empty feature code", targetFont=None, codeSig="DEFAULT-CODE-SIGNATURE", createSeparateEntry=False):
	"""
	Creates or updates an OpenType feature in the font.
	Returns a status message in form of a string.
	featureName: name of the feature (str),
	featureCode: the AFDKO feature code (str),
	targetFont: the GSFont object receiving the feature (defaults to Glyphs.font),
	codeSig: the code signature (str) used as # BEGIN/# END delimiters for easy updating,
	createSeparateEntry: if True, adds a separate feature entry rather than reusing an existing one.
	"""
	if targetFont is None:
		targetFont = Glyphs.font
	if targetFont is None:
		return "🛑 ERROR: Could not create OT feature %s. No font detected." % featureName

	beginSig = "# BEGIN " + codeSig + "\n"
	endSig = "# END " + codeSig + "\n"

	featuresWithTag = [f for f in targetFont.features if f.name == featureName and f.name]
	featureExists = len(featuresWithTag) > 0
	featuresWithSig = [f for f in targetFont.features if beginSig in f.code and endSig in f.code and f.active]
	sigExists = len(featuresWithSig) > 0

	if sigExists:
		for targetFeature in featuresWithSig:
			# replace old code with new code:
			targetFeature.code = updatedCode(targetFeature.code, beginSig, endSig, featureCode)
		return "✅ Updated %i existing OT feature%s ‘%s’." % (
			len(featuresWithSig),
			"" if len(featuresWithSig) == 1 else "s",
			featureName,
		)
	elif featureExists and not createSeparateEntry:
		# feature already exists:
		targetFeature = targetFont.features[featureName]  # take the first available one
		targetFeature.code += "\n" + beginSig + featureCode + "\n" + endSig
		return "✅ Added code to first available OT feature ‘%s’." % featureName
	else:
		# create feature with new code:
		newFeature = GSFeature()
		newFeature.name = featureName
		newFeature.code = beginSig + featureCode + "\n" + endSig
		targetFont.features.append(newFeature)
		return "🌟 Created new OT feature entry ‘%s’" % featureName


def createOTClass(className="@default", classGlyphNames=None, targetFont=None, automate=False):
	"""
	Creates or updates an OpenType class in the font.
	Returns a status message in form of a string.
	className: name of the OT class, with or without a leading at sign,
	classGlyphNames: list of glyph names (defaults to the current selection),
	targetFont: the GSFont that receives the OT class (defaults to Glyphs.font),
	automate: if True, marks the class as automatically generated when possible.
	"""
	if targetFont is None:
		targetFont = Glyphs.font
	if classGlyphNames is None and targetFont is not None:
		classGlyphNames = [layer.parent.name for layer in targetFont.selectedLayers]

	if targetFont is None or not (classGlyphNames or automate):
		return "🛑 ERROR: Could not create OT class %s. Missing either font or glyph names, or both." % className

	className = className.lstrip("@")  # strip '@' from beginning
	classCode = " ".join(classGlyphNames)
	otClass = None

	# build or update class:
	if className in [c.name for c in targetFont.classes]:
		otClass = targetFont.classes[className]
		otClass.code = classCode
		returnText = "✅ Updated existing OT class ‘%s’." % className
	else:
		otClass = GSClass()
		otClass.name = className
		otClass.code = classCode
		targetFont.classes.append(otClass)
		returnText = "🌟 Created new OT class: ‘%s’" % className

	# automate the class:
	if automate and otClass is not None:
		if Glyphs.versionNumber >= 3:
			if otClass.canBeAutomated():
				otClass.automatic = True
		else:
			otClass.automatic = True
		returnText = returnText.rstrip(".") + " (automated)."

	return returnText


class mekkaObject:
	prefDict = None
	w = None

	def domain(self, prefName: str) -> str:
		prefName = prefName.strip().strip(".")
		return "com.mekkablue." + self.__class__.__name__ + "." + prefName.strip()

	def pref(self, prefName: str) -> Any:
		prefDomain = self.domain(prefName)
		# print(prefName, "-> getting domain", prefDomain, "<<<")  # DEBUG
		prefValue = Glyphs.defaults[prefDomain]
		if prefValue is not None:  # can be 0, False, an empty collection or an empty string too
			return prefValue
		return self.prefDict.get(prefName, None)

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
				element = self.uiElement(prefName)
				element.set(self.pref(prefName))
				# configure text fields: clip mid-character (don't hide whole words),
				# and suppress macOS autofill popups
				if hasattr(element, "getNSTextField"):
					nsField = element.getNSTextField()
					nsField.cell().setScrollable_(True)
					nsField.cell().setLineBreakMode_(NSLineBreakByClipping)
					if hasattr(nsField, "setContentType_"):
						nsField.setContentType_(None)
			if hasattr(self, "updateUI"):
				self.updateUI()
			if self.w is not None:
				# AppKit restores the autosaved frame only when open() is called, not at
				# window creation. Wrap open() so the clamp fires after the frame is restored.
				# Guard against double-wrapping if LoadPreferences() is called more than once.
				if not getattr(self.w, '_clampOnOpenInstalled', False):
					_originalOpen = self.w.open
					_self = self

					def _openAndClamp():
						_originalOpen()
						_self.resizeWindowToMinimum()

					self.w.open = _openAndClamp
					self.w._clampOnOpenInstalled = True
			return True
		except:
			import traceback
			print(traceback.format_exc())
			print(f"⚠️ ‘{self.__class__.__name__}’ could not load preferences. Will resort to defaults.")
			return False

	def resizeWindowToMinimum(self):
		"""
		Clamps the window size to its min/max constraints, per axis independently.
		Uses contentMinSize()/contentMaxSize() so the comparison is in content coordinates,
		matching getPosSize() — no manual title-bar offset needed.
		"""
		win = self.w._window
		minSize = win.contentMinSize()
		maxSize = win.contentMaxSize()
		currentWidth, currentHeight = self.w.getPosSize()[2], self.w.getPosSize()[3]
		clampedWidth = max(minSize.width, min(currentWidth, maxSize.width))
		clampedHeight = max(minSize.height, min(currentHeight, maxSize.height))
		if clampedWidth != currentWidth or clampedHeight != currentHeight:
			self.w.resize(clampedWidth, clampedHeight, animate=False)

	def SavePreferences(self, sender=None):
		try:
			# write current settings into prefs:
			for prefName in self.prefDict.keys():
				Glyphs.defaults[self.domain(prefName)] = self.uiElement(prefName).get()
			if hasattr(self, "updateUI"):
				self.updateUI()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			print(f"⚠️ ‘{self.__class__.__name__}’ could not write preferences.")
			return False
