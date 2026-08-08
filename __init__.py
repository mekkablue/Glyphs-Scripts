
from math import ceil
from typing import Any
from AppKit import NSUserDefaults, NSFont, NSImage, NSImageLeading, NSMakeSize, NSPasteboard, NSStringPboardType, NSLineBreakByClipping
from GlyphsApp import Glyphs, GSFeature, GSClass, GSControlLayer, GSGlyph
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


def resolvedAttribute(obj, attributeNames, default=None):
	"""
	Returns the value of the first of attributeNames that the object has.
	Depending on the Glyphs version, the same information is exposed either as a
	pyobjc method or as a plain python property, so both are resolved here.
	attributeNames can be a single name or a tuple of names to try in order.
	"""
	if isinstance(attributeNames, str):
		attributeNames = (attributeNames, )
	for attributeName in attributeNames:
		value = getattr(obj, attributeName, None)
		if value is None:
			continue
		if callable(value):
			try:
				value = value()
			except TypeError:
				pass
		if value is not None:
			return value
	return default


def particleName(particle):
	"""Returns the name of a GSNameParticle (Glyphs 4) as a string, empty string if it has none."""
	return str(resolvedAttribute(particle, "name", ""))


def particleAxisValue(particle):
	"""
	Returns the axis value of a GSNameParticle (Glyphs 4) as a float. A particle
	carries an internal (design space) and an external (user space) value, and
	the external one is optional, so fall back to the internal value if it is
	missing. Returns None if neither value is set.
	"""
	for attributeNames in (("externalValue", "external"), ("internalValue", "internal")):
		value = resolvedAttribute(particle, attributeNames)
		if value is not None:
			try:
				return float(value)
			except (TypeError, ValueError):
				pass
	return None


def nameParticlesOfInstance(instance):
	"""
	Returns the name particles of a Glyphs 4 particle instance (a mapping of
	axisId → list of GSNameParticle), or None if the instance has none.
	Depending on the Glyphs version, instance.nameParticles is either a pyobjc
	method or a (dict-like) proxy object, so both are resolved here.
	"""
	nameParticles = getattr(instance, "nameParticles", None)
	if callable(nameParticles):
		try:
			return nameParticles()
		except TypeError:
			pass
	return nameParticles


def nameParticleAxisIDs(instance):
	"""
	Returns a list of the axisIds for which the instance carries name particles.
	Empty list if there are none.
	"""
	nameParticles = nameParticlesOfInstance(instance)
	if not nameParticles:
		return []
	for accessor in ("allKeys", "keys"):
		method = getattr(nameParticles, accessor, None)
		if callable(method):
			try:
				return list(method())
			except TypeError:
				pass
	try:
		return list(nameParticles)
	except TypeError:
		return []


def nameParticlesForAxisID(instance, axisID):
	"""
	Returns the name particles of the instance for the axis with the given
	axisId, or None if there are none. Works with both dicts and the
	proxy objects that Glyphs returns for instance.nameParticles.
	"""
	nameParticles = nameParticlesOfInstance(instance)
	if not nameParticles:
		return None
	getter = getattr(nameParticles, "get", None)
	if callable(getter):
		try:
			return getter(axisID)
		except TypeError:
			pass
	objectForKey = getattr(nameParticles, "objectForKey_", None)
	if objectForKey is not None:
		try:
			return objectForKey(axisID)
		except TypeError:
			pass
	try:
		return nameParticles[axisID]
	except (KeyError, IndexError, TypeError):
		return None


def newLineControlLayer():
	"""
	Returns a GSControlLayer representing a newline, for inserting line breaks
	into tab.layers.
	Temporary workaround: in some Glyphs versions, GSControlLayer.newline() raises
	'TypeError: GSControlLayer() does not accept positional arguments', because it
	internally calls GSControlLayer(10). In that case, we fall back to the ObjC
	initializer.
	"""
	try:
		return GSControlLayer.newline()
	except TypeError:
		return GSControlLayer.alloc().initWithChar_(10)


def newGlyphWithName(glyphName):
	"""
	Returns a new GSGlyph carrying the supplied name.
	Temporary workaround: in some Glyphs versions, GSGlyph("name") raises
	'TypeError: GSGlyph() does not accept positional arguments'. In that case,
	we create the glyph without arguments and set its name afterwards.
	"""
	try:
		return GSGlyph(glyphName)
	except TypeError:
		glyph = GSGlyph()
		glyph.name = glyphName
		return glyph


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


def measureButtons(buttons, minButtonWidth=70, minHeight=20):
	"""
	Measures the sizes vanilla Buttons need on the running system.
	Returns (widths, height): a list with one width per button, and the height
	of the tallest one. Sizes are taken from the button cells, so they follow
	the button metrics of the macOS version the script is running on.
	"""
	widths = []
	height = minHeight
	for button in buttons:
		nsButton = button.getNSButton()
		nsButton.sizeToFit()
		sizes = [nsButton.fittingSize(), nsButton.frame().size]
		try:
			sizes.append(nsButton.cell().cellSize())
			sizes.append(nsButton.intrinsicContentSize())
		except:
			pass
		widths.append(max(minButtonWidth, ceil(max(size.width for size in sizes))))
		height = max(height, ceil(max(size.height for size in sizes)))
	return widths, height


def alignButtons(window, rightButtons=(), leftButtons=(), inset=15, gap=10, leftGap=None, minButtonWidth=70, assumedHeight=20, resizeWindow=True):
	"""
	Lays out one or two groups of vanilla Buttons along the bottom edge of window:
	rightButtons are right-aligned, leftButtons are left-aligned. Each button gets
	the size it actually needs on the running system, rather than a hardcoded one.
	Necessary because push buttons became larger in recent macOS versions, which
	made hardcoded button rows collide.
	Recent macOS also draws the button bezel *beyond* the button frame. The overhang
	is derived from how much taller the buttons are than assumedHeight, and added to
	the gaps and the window edge distances, so that the drawn (not the theoretical)
	buttons keep their distances. On older macOS, the overhang is zero and the layout
	is the same as before.
	window: the vanilla window containing the buttons,
	rightButtons: the vanilla Buttons for the bottom right, in left-to-right order,
	leftButtons: the vanilla Buttons for the bottom left, in left-to-right order,
	inset: distance to the window edges,
	gap: visible horizontal distance between two buttons,
	leftGap: same, but for the leftButtons group only; defaults to gap,
	minButtonWidth: no button will be narrower than this,
	assumedHeight: the button height the rest of the window layout was built for,
	resizeWindow: if True, grows the window (and its size constraints) to fit the row.
	Returns (rowWidth, rowHeight), or None if the measurement failed.
	"""
	try:
		if leftGap is None:
			leftGap = gap
		rightWidths, height = measureButtons(rightButtons, minButtonWidth, assumedHeight)
		leftWidths, height = measureButtons(leftButtons, minButtonWidth, height)

		# how far the drawn bezel extends beyond the button frame on each side:
		overhang = max(0, (height - assumedHeight) // 2)
		bottomInset = inset + overhang
		sideInset = inset + overhang
		rightStep = gap + 2 * overhang  # frame distance yielding a visible distance of gap
		leftStep = leftGap + 2 * overhang

		rowWidth = sum(rightWidths) + sum(leftWidths) + 2 * overhang
		if rightWidths:
			rowWidth += rightStep * (len(rightWidths) - 1)
		if leftWidths:
			rowWidth += leftStep * (len(leftWidths) - 1)
		if rightWidths and leftWidths:
			rowWidth += rightStep  # minimum distance between the two groups
		rowHeight = height + 2 * overhang

		if resizeWindow:
			windowWidth, windowHeight = window.getPosSize()[2], window.getPosSize()[3]
			deltaWidth = max(0, rowWidth + 2 * inset - windowWidth)
			deltaHeight = max(0, rowHeight - assumedHeight)
			if deltaWidth or deltaHeight:
				nsWindow = window._window
				for getter, setter in (
					(nsWindow.contentMinSize, nsWindow.setContentMinSize_),
					(nsWindow.contentMaxSize, nsWindow.setContentMaxSize_),
				):
					currentSize = getter()
					setter(NSMakeSize(currentSize.width + deltaWidth, currentSize.height + deltaHeight))
				window.resize(windowWidth + deltaWidth, windowHeight + deltaHeight, animate=False)

		# right group, positioned right to left:
		rightEdge = sideInset
		for button, width in zip(reversed(rightButtons), reversed(rightWidths)):
			button.setPosSize((-rightEdge - width, -height - bottomInset, width, height))
			rightEdge += width + rightStep

		# left group, positioned left to right:
		leftEdge = sideInset
		for button, width in zip(leftButtons, leftWidths):
			button.setPosSize((leftEdge, -height - bottomInset, width, height))
			leftEdge += width + leftStep

		return rowWidth, rowHeight
	except:
		import traceback
		print(traceback.format_exc())
		print("⚠️ Could not align buttons, will resort to their original positions.")
		return None


def alignButtonsRight(window, buttons, inset=15, gap=10, minButtonWidth=70, assumedHeight=20, resizeWindow=True):
	"""
	Lays out a row of vanilla Buttons right-aligned along the bottom edge of window.
	Shortcut for alignButtons() with a right group only; see there for details.
	"""
	return alignButtons(
		window,
		rightButtons=buttons,
		inset=inset,
		gap=gap,
		minButtonWidth=minButtonWidth,
		assumedHeight=assumedHeight,
		resizeWindow=resizeWindow,
	)


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
