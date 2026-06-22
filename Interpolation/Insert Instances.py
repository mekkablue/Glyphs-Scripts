# MenuTitle: Insert Instances
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Inserts instances, based on the Luc(as), Pablo, Abraham, Schneider and Maciej algorithms.
In Glyphs 4+, presents a redesigned UI for inserting axis particles.
"""

from Foundation import NSDictionary
import vanilla
from GlyphsApp import Glyphs, GSInstance, INSTANCETYPESINGLE
from mekkablue import mekkaObject, UpdateButton

rangemin = 3
rangemax = 11

naturalNames = (
	"Hairline",
	"Thin",
	"Extralight",
	"Light",
	"Regular",
	"Medium",
	"Semibold",
	"Bold",
	"Extrabold",
	"Black",
	"Extrablack",
)

weightClasses = {
	"Hairline": 1,
	"Thin": 100,
	"Extralight": 200,
	"Light": 300,
	"Regular": 400,
	"Medium": 500,
	"Semibold": 600,
	"Bold": 700,
	"Extrabold": 800,
	"Black": 900,
	"Extrablack": 1000,
}

weightClassesOldNames = {
	"Hairline": "Thin:1",
	"Thin": "Thin",
	"Extralight": "ExtraLight",
	"Light": "Light",
	"Regular": "Regular",
	"Medium": "Medium",
	"Semibold": "SemiBold",
	"Bold": "Bold",
	"Extrabold": "ExtraBold",
	"Black": "Black",
	"Extrablack": "Black:1000",
}


distributionExplanation = """
The way the Weight values are distributed between the first and last master values you entered above. Linear means equal steps between instances. Luc(as) (after Lucas de Groot) means the same growth percentage between instances. Pablo (after Pablo Impallari) is like Luc(as) at first, then becomes increasingly linear, i.e., flat in the periphery and steep in the middle. Schneider (after Lukas Schneider) is half way between Pablo and Luc(as) algorithms. Abraham (after Abraham Lee) is linear at first, then becomes increasingly like Luc(as), i.e. steep in the periphery, flat in the middle.

For medium weights, you typically want bigger steps. Smaller jumps are preferable in the periphery, i.e., for very light and very dark weights.

So, for a wide spectrum from very light to very bold, try Pablo, Schneider, or Mirrored Luc(as).

For spectrums from thin to medium weights, try Abraham or Luc(as). They tend to have large jumps at the end, which are usually found in the center of the weight spectrum (Regular to Semibold).

For going from medium to very bold weights, try Reverse Luc(as). It has big jumps at the beginning, and smaller steps at the end.
"""

distributionNames = ("linear", "Pablo", "Schneider", "Abraham", "Luc(as)", "Reverse Luc(as)", "Mirrored Luc(as)")


def distribute_lucas(min, max, n):
	if min == 0:
		min = max / 1000.0
	q = max / min
	return [min * q**(i / (n - 1)) for i in range(n)]


def distribute_reverselucas(min, max, n):
	if min == 0:
		min = max / 1000.0
	q = max / min
	return [min + max - min * q**(i / (n - 1)) for i in range(n - 1, -1, -1)]


def distribute_mirroredlucas(min, max, n):
	center = (min + max) / 2
	if n % 2 == 1:
		n2 = (n + 1) // 2
		return distribute_lucas(min, center, n2) + distribute_reverselucas(center, max, n2)[1:]
	else:
		deviation = ((max - min) / (n - 1)) / 2
		return distribute_lucas(min, center - deviation, n // 2) + distribute_reverselucas(center + deviation, max, n // 2)


def distribute_equal(min, max, n):
	d = (max - min) / (n - 1)
	return [min + i * d for i in range(n)]


def distribute_pablo(min, max, n):
	es = distribute_equal(min, max, n)
	ls = distribute_lucas(min, max, n)
	return [l * (1 - i / (n - 1)) + e * (i / (n - 1)) for (i, e, l) in zip(range(n), es, ls)]


def distribute_schneider(min, max, n):
	ps = distribute_pablo(min, max, n)
	ls = distribute_lucas(min, max, n)
	return [(p + l) * 0.5 for (p, l) in zip(ps, ls)]


def distribute_abraham(min, max, n):
	es = distribute_equal(min, max, n)
	ls = distribute_lucas(min, max, n)
	return [e * (1 - (i / (n - 1))**1.25) + l * (i / (n - 1))**1.25 for (i, e, l) in zip(range(n), es, ls)]


def distribute_maciej(lightMasterWeightX, lightMasterWeightY, boldMasterWeightX, boldMasterWeightY, interpolationWeightX):
	"""
	Algorithm by Maciej Ratajski
	https://jsfiddle.net/Dm2Zk/1/
	"""
	interpolationPointX = (interpolationWeightX - lightMasterWeightX) / (boldMasterWeightX - lightMasterWeightX)
	interpolationWeightY = ((1 - interpolationPointX) * (lightMasterWeightY / lightMasterWeightX - boldMasterWeightY / boldMasterWeightX) + boldMasterWeightY / boldMasterWeightX) * interpolationWeightX
	interpolationPointY = (interpolationWeightY - lightMasterWeightY) / (boldMasterWeightY - lightMasterWeightY)
	return round((boldMasterWeightX - lightMasterWeightX) * interpolationPointY + lightMasterWeightX, 1)


def applyDistribution(algorithmName, axisMin, axisMax, n):
	if n < 2:
		return [axisMin]
	if algorithmName == "Pablo":
		return distribute_pablo(axisMin, axisMax, n)
	elif algorithmName == "Luc(as)":
		return distribute_lucas(axisMin, axisMax, n)
	elif algorithmName == "Reverse Luc(as)":
		return distribute_reverselucas(axisMin, axisMax, n)
	elif algorithmName == "Mirrored Luc(as)":
		return distribute_mirroredlucas(axisMin, axisMax, n)
	elif algorithmName == "Schneider":
		return distribute_schneider(axisMin, axisMax, n)
	elif algorithmName == "Abraham":
		return distribute_abraham(axisMin, axisMax, n)
	else:
		return distribute_equal(axisMin, axisMax, n)


def axisLocationEntry(axisName, locationValue):
	return NSDictionary.alloc().initWithObjects_forKeys_((axisName, locationValue), ("Axis", "Location"))


def _safeAttrName(tag):
	"""Convert axis tag to a safe Python identifier for use as an attribute name."""
	return "".join(c if c.isalnum() or c == "_" else "_" for c in tag)


class InstanceMaker(mekkaObject):
	"""GUI for injecting instances."""
	prefDict = {
		"numberOfInstances": "6",
		"prefix": "",
		"master1": 1,  # self.MasterList(1),
		"master2": -1,  # self.MasterList(-1),
		"width": "100",
		"algorithm": 0,
		"existingInstances": False,
		"maciej": False,
		"maciej_light": 1,  # self.MasterList(1),
		"maciej_bold": -1,  # self.MasterList(-1),
		"shouldRound": True,
		"naturalNames": True,
		"firstName": 1,
		"italicStyle": False,
		"keepWindowOpen": 1,
		"axisLocation": 1,
		"axisLocationMaster": 1,
	}

	def __init__(self):

		# Window 'self.w':
		windowWidth = 360
		windowHeight = 400
		windowWidthResize = 0  # user can resize width by this value
		windowHeightResize = 300  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Insert weight instances",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		linePos, inset, lineHeight = 12, 15, 26

		self.w.text_1 = vanilla.TextBox((inset - 1, linePos + 2, 35, 14), "Insert", sizeStyle='small')
		self.w.numberOfInstances = vanilla.PopUpButton((inset + 37, linePos, 40, 17), [str(x) for x in range(3, 12)], callback=self.UpdateSample, sizeStyle='small')
		self.w.numberOfInstances.setToolTip("Choose how many weights you want to add.")
		self.w.text_2 = vanilla.TextBox((inset + 30 + 50, linePos + 2, 105, 14), "weights with prefix", sizeStyle='small')
		self.w.prefix = vanilla.EditText((inset + 30 + 50 + 105, linePos - 1, -inset, 19), "A-", callback=self.UpdateSample, sizeStyle='small')
		self.w.prefix.setToolTip("Choose text that is added at the beginning of each instance, e.g., 'Condensed'.")
		linePos += lineHeight

		self.w.text_3 = vanilla.TextBox((inset - 1, linePos + 2, 60, 14), "from:", sizeStyle='small')
		self.w.master1 = vanilla.ComboBox((inset + 35, linePos - 1, 62, 19), self.MasterList(1), callback=self.UpdateSample, sizeStyle='small')
		self.w.master1.setToolTip("Weight value for the first instance being added, typically the stem width of your lightest weight.")
		self.w.text_4 = vanilla.TextBox((inset + 50 + 55 * 1, linePos + 2, 55, 14), "through:", sizeStyle='small')
		self.w.master2 = vanilla.ComboBox((inset + 50 + 55 * 2, linePos - 1, 62, 19), self.MasterList(-1), callback=self.UpdateSample, sizeStyle='small')
		self.w.master2.setToolTip("Weight value for the last instance being added, typically the stem width of your boldest weight.")
		self.w.text_5 = vanilla.TextBox((inset + 65 + 55 * 3, linePos + 2, 55, 14), "at width:", sizeStyle='small')
		self.w.width = vanilla.EditText((inset + 65 + 55 * 4, linePos - 1, -inset, 19), "100", callback=self.UpdateSample, sizeStyle='small')
		self.w.width.setToolTip("The Width value for the instances being added. Default is 100. Adapt accordingly if you are adding condensed or extended instances.")
		linePos += lineHeight

		self.w.text_6 = vanilla.TextBox((inset - 1, linePos + 2, 60, 14), "using", sizeStyle='small')
		self.w.algorithm = vanilla.PopUpButton((inset + 35, linePos, 125, 17), ("linear", "Pablo", "Schneider", "Abraham", "Luc(as)", "Reverse Luc(as)", "Mirrored Luc(as)"), callback=self.UpdateSample, sizeStyle='small')
		self.w.algorithm.setToolTip(distributionExplanation)
		self.w.text_7 = vanilla.TextBox((inset + 40 + 125, linePos + 2, 110, 14), "distribution.", sizeStyle='small')
		self.w.help_instances = vanilla.HelpButton((-15 - 21, linePos + 2, -inset, 20), callback=self.openURL)
		linePos += lineHeight

		self.w.existingInstances = vanilla.RadioGroup((inset + 20, linePos, -10, 60), ("Leave existing instances as they are", "Deactivate existing instances", "Delete existing instances"), callback=self.SavePreferences, sizeStyle='small')
		self.w.existingInstances.set(0)
		linePos += int(lineHeight * 2.4)

		self.w.naturalNames = vanilla.CheckBox((inset + 2, linePos, inset + 225, 19), "Use 'natural' weight names, starting at:", value=False, callback=self.UpdateSample, sizeStyle='small')
		self.w.naturalNames.setToolTip("Prefill with standard names and style linking. If turned off, will use the Weight number as instance name.")
		self.w.firstName = vanilla.PopUpButton((inset + 225, linePos, -inset, 17), naturalNames, callback=self.UpdateSample, sizeStyle='small')
		self.w.firstName.setToolTip("If you use natural weight names, choose here the name of your lightest weight.")
		try:  # workaround for macOS 10.9
			self.w.firstName.enable(self.w.naturalNames.getNSButton().isEnabled())
		except:
			pass
		linePos += lineHeight - 8

		if Glyphs.versionNumber >= 3:
			self.w.axisLocation = vanilla.CheckBox((inset + 20, linePos, 220, 20), "Set Axis Location for each instance", value=True, callback=self.SavePreferences, sizeStyle='small')
			self.w.axisLocationMaster = vanilla.CheckBox((inset + 227, linePos, -inset, 20), "and master", value=True, callback=self.SavePreferences, sizeStyle='small')
			self.w.axisLocation.setToolTip("If enabled, will add an Axis Location parameter with the proper usWeightClass value in Font Info → Exports.\n\nHINT: Do not forget to set Axis Location parameters for each master in Font Info → Masters, and remove the Axis Mappings parameter in Font Info → Font if you have one.")
			self.w.axisLocationMaster.setToolTip("If enabled, will attempt to set Axis Locations for masters as well. Only works if there is an instance that matches the respective master.")
			linePos += lineHeight - 8

		self.w.italicStyle = vanilla.CheckBox((inset + 20, linePos, -inset, 20), "Italic suffixes and style linking", value=False, callback=self.UpdateSample, sizeStyle='small')
		self.w.italicStyle.setToolTip("If enabled, will add the word 'Italic' to all instances, and also add italic style linking.")
		linePos += lineHeight

		self.w.maciej = vanilla.CheckBox((inset + 2, linePos - 1, 160, 19), "Maciej y distribution from:", value=False, callback=self.UpdateSample, sizeStyle='small')
		self.w.maciej.setToolTip("An algorithm proposed by Maciej Ratajski, which introduces slightly different interpolation for y coordinates. Will add interpolationWeightY parameters to the instances. If these value differ greatly from the weight interpolation values, interpolation of your diagonals may suffer.")
		self.w.text_maciej_1 = vanilla.TextBox((inset + 165 + 55, linePos + 2, 55, 19), "through:", sizeStyle='small')
		self.w.maciej_light = vanilla.ComboBox((inset + 160, linePos - 1, 55, 19), self.MasterList(1), callback=self.UpdateSample, sizeStyle='small')
		self.w.maciej_bold = vanilla.ComboBox((inset + 160 + 55 + 55, linePos - 1, -inset, 19), self.MasterList(-1), callback=self.UpdateSample, sizeStyle='small')
		linePos += lineHeight - 6

		self.w.text_maciej_2 = vanilla.TextBox((inset + 15, linePos, -40, 40), "Provide horizontal stem widths in extreme masters to interpolate contrast rather than stems.", sizeStyle='small', selectable=True)
		self.w.help_maciej = vanilla.HelpButton((-inset - 21, linePos + 4, -inset, 20), callback=self.openURL)
		self.w.help_maciej.setToolTip("Will open a website with a detailed description of the Maciej algorithm. Requires an internet connection.")
		linePos += int(lineHeight * 1.2)

		self.w.shouldRound = vanilla.CheckBox((inset + 2, linePos, 200, 20), "Round all interpolation values", value=True, callback=self.UpdateSample, sizeStyle='small')
		self.w.shouldRound.setToolTip("If enabled, will round all calculated weight values to integers. Usually a good idea.")

		self.w.keepWindowOpen = vanilla.CheckBox((inset + 200, linePos, -inset, 20), "Keep window open", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.keepWindowOpen.setToolTip("If checked, will not close this window after applying the distribution.")
		linePos += lineHeight

		self.w.sample = vanilla.Box((inset, linePos, -inset, -30 - inset))
		self.w.sample.text = vanilla.TextBox((5, 5, -5, -5), "", sizeStyle='small')

		# buttons:
		self.w.createButton = vanilla.Button((-80 - inset, -20 - inset, -inset, -inset), "Insert", callback=self.CreateInstances)
		self.w.setDefaultButton(self.w.createButton)

		self.LoadPreferences()

		self.w.open()
		self.UpdateSample(self)
		self.w.makeKey()

	def axisTag(self, axis):
		if Glyphs.versionNumber >= 3:
			# Glyphs 3 code
			return axis.axisTag
		else:
			# Glyphs 2 code
			return axis["Tag"]

	def axisID(self, axis):
		if Glyphs.versionNumber >= 3:
			# Glyphs 3 code
			return axis.axisId
		else:
			# Glyphs 2 code
			# Glyphs 2 axis doesn't have an id
			return None

	def weightID(self, thisFont):
		weightAxisID = None
		if thisFont.axes:
			weightAxis = thisFont.axes[0]  # default
			weightAxisID = self.axisID(weightAxis)
			for axis in thisFont.axes:
				axisTag = self.axisTag(axis)
				if axisTag == "wght":
					weightAxisID = self.axisID(axis)
		return weightAxisID

	def widthID(self, thisFont):
		widthAxisID = None  # None
		for axis in thisFont.axes:
			if self.axisTag(axis) == "wdth":
				widthAxisID = self.axisID(axis)
		return widthAxisID

	def MasterList(self, factor):
		thisFont = Glyphs.font
		MasterValues = ()
		if thisFont:
			try:
				# GLYPHS 3:
				if thisFont.axes:
					weightAxisID = self.weightID(thisFont)
					if weightAxisID:
						MasterValues = sorted(set([m.axisValueValueForId_(weightAxisID) for m in thisFont.masters]), key=lambda m: m * factor)
			except:
				# GLYPHS 2:
				import traceback
				print(traceback.format_exc())
				MasterValues = sorted([m.weightValue for m in thisFont.masters], key=lambda m: m * factor)

		return MasterValues

	def Distribution(self):
		a = float(self.w.master1.get())
		b = float(self.w.master2.get())
		n = int(self.w.numberOfInstances.getItems()[self.w.numberOfInstances.get()])

		algorithm = self.w.algorithm.getItems()[self.w.algorithm.get()]
		if algorithm == "Pablo":
			distributedValues = distribute_pablo(a, b, n)
		elif algorithm == "Luc(as)":
			distributedValues = distribute_lucas(a, b, n)
		elif algorithm == "Reverse Luc(as)":
			distributedValues = distribute_reverselucas(a, b, n)
		elif algorithm == "Mirrored Luc(as)":
			distributedValues = distribute_mirroredlucas(a, b, n)
		elif algorithm == "Schneider":
			distributedValues = distribute_schneider(a, b, n)
		elif algorithm == "Abraham":
			distributedValues = distribute_abraham(a, b, n)
		else:
			distributedValues = distribute_equal(a, b, n)

		return distributedValues

	def UpdateSample(self, sender=None):
		# Query UI entries and write preview text
		self.SavePreferences()

		try:
			usesNaturalNames = self.pref("naturalNames")

			# update UI elements:
			if usesNaturalNames:
				currentSelectionIndex = self.pref("firstName")
				numOfInstances = int(self.w.numberOfInstances.getItem())
				availableInstanceNames = naturalNames[:-numOfInstances + 1]
				numOfAvailableInstanceNames = len(availableInstanceNames)
				self.w.firstName.setItems(availableInstanceNames)
				if not currentSelectionIndex < len(availableInstanceNames):
					self.w.firstName.set(numOfAvailableInstanceNames - 1)
				else:
					self.w.firstName.set(currentSelectionIndex)
				self.w.firstName.enable(True)
			else:
				self.w.firstName.enable(False)

			# store UI changes in defaults:
			self.SavePreferences()

			if self.pref("shouldRound"):
				rounding = 0
			else:
				rounding = 1

			distributedValues = [round(value, rounding) for value in self.Distribution()]
			n = len(distributedValues)
			prefix = self.pref("prefix")
			sampleText = "Will create %i instances: " % n

			if usesNaturalNames:
				sampleText += ", ".join(
					"%s (%.01f)" % (self.completeStyleName(prefix, self.italicStyleName(name)), weight) for name, weight in zip(naturalNames[currentSelectionIndex:], distributedValues)
				)
			else:
				sampleText += ", ".join(
					"%s (%.01f)" % (self.completeStyleName(prefix, "%.0f" % weight), weight) for weight in distributedValues
				)

			max = float(distributedValues[-1])
			min = float(distributedValues[0])
			growth = (max / min)**(1.0 / (n - 1))
			if self.w.algorithm.getItem() == "Luc(as)":
				sampleText += ",%s growth: %.1f%%" % (
					" average" if self.pref("shouldRound") else "",
					(growth - 1) * 100,
				)

			if self.pref("maciej"):
				maciejValues = self.MaciejValues()
				if maciejValues:
					maciejList = [str(round(distribute_maciej(maciejValues[0], maciejValues[1], maciejValues[2], maciejValues[3], w), rounding)) for w in distributedValues]
					sampleText += "\n\nWill add interpolationWeightY parameters to instances: %s" % (", ".join(maciejList) + ".")

			self.w.sample.text.set(sampleText)
		except Exception as e:
			print(e)

	def DealWithExistingInstances(self):
		instancesChoice = self.w.existingInstances.get()
		if instancesChoice == 1:  # deactivate
			for thisInstance in Glyphs.font.instances:
				if Glyphs.buildNumber > 3198:
					thisInstance.exports = False
				else:
					thisInstance.active = False
		elif instancesChoice == 2:  # delete
			if Glyphs.versionNumber >= 3:
				# GLYPHS 3
				Glyphs.font.instances = [i for i in Glyphs.font.instances if i.type != INSTANCETYPESINGLE]
			else:
				# GLYPHS 2
				Glyphs.font.instances = None
		return True

	def updateUI(self, sender=None):
		# Natural names:
		onOff = self.pref("naturalNames")
		self.w.italicStyle.enable(onOff)
		if Glyphs.versionNumber >= 3:
			self.w.axisLocation.enable(onOff)

		# Maciej:
		onOff = self.pref("maciej")
		self.w.text_maciej_1.enable(onOff)
		self.w.maciej_light.enable(onOff)
		self.w.maciej_bold.enable(onOff)

		# axis locations for master:
		onOff = self.pref("axisLocation")
		self.w.axisLocationMaster.enable(onOff)

	def openURL(self, sender):
		URL = None
		if sender == self.w.help_instances:
			URL = "https://www.glyphsapp.com/learn/multiple-masters-part-3-setting-up-instances"
		if sender == self.w.help_maciej:
			URL = "https://web.archive.org/web/20171017001354/https://www.maciejratajski.com/theory/interpolation-of-contrast"
			# URL = "https://www.maciejratajski.com/theory/interpolation-of-contrast/"
		if URL:
			import webbrowser
			webbrowser.open(URL)

	def MaciejValues(self):
		lightX = float(self.w.master1.get())
		boldX = float(self.w.master2.get())
		lightY = float(self.w.maciej_light.get())
		boldY = float(self.w.maciej_bold.get())
		if lightX and boldX and lightY and boldY:
			return [lightX, lightY, boldX, boldY]
		else:
			return False

	def completeStyleName(self, prefix, name, elidableName="Regular", naturalNames=True):
		# e.g. "A-160"
		if not naturalNames:
			return prefix + name

		# elidable
		if prefix.strip() and name == elidableName:
			return prefix.strip()

		particles = name.strip().split(" ")
		if prefix.strip() != "":
			particles.insert(0, prefix.strip())

		if len(particles) == 0:
			# elidable fallback name
			return elidableName
		elif len(particles) > 1 and elidableName in particles:
			# remove elidable particle
			while elidableName in particles:
				particles.remove(elidableName)

		return " ".join(particles).strip()

	def italicStyleName(self, styleName):
		if self.pref("italicStyle"):
			styleName = "%s Italic" % styleName
			styleName = styleName.replace("Regular Italic", "Italic")
		return styleName

	def CreateInstances(self, sender):
		try:
			theFont = Glyphs.font
			paramName = "Axis Location"

			if self.DealWithExistingInstances():
				distributedValues = self.Distribution()
				try:
					widthValue = self.prefFloat("width")
				except:
					widthValue = 100.0
				prefix = self.pref("prefix")
				maciejYesOrNo = self.pref("maciej")
				roundingYesOrNo = self.pref("shouldRound")

				if maciejYesOrNo:
					maciejValues = self.MaciejValues()
					# invalid if entered values are empty or invalid:
					if not maciejValues:
						maciejYesOrNo = False

				# numOfInstances = self.prefInt("numberOfInstances")
				currentSelectionIndex = self.prefInt("firstName")
				instanceNames = naturalNames[currentSelectionIndex:]

				for i, thisWeight in enumerate(distributedValues):
					if roundingYesOrNo:
						thisWeight = round(thisWeight)

					# create new instance:
					newInstance = GSInstance()
					newInstance.active = True
					weightClassValue = None

					# determine names, style linking, weight class, etc.:
					if self.pref("naturalNames"):
						# weight style name (no italic)
						styleName = instanceNames[i]

						# weightclass
						weightClassOldName = weightClassesOldNames[styleName]
						weightClassValue = weightClasses[styleName]
						if ":" in weightClassOldName:
							weightClassValue = int(weightClassOldName.split(":")[1].strip())
							weightClassOldName = weightClassOldName.split(":")[0].strip()

						try:
							# GLYPHS 3:
							newInstance.setWeightClassValue_(weightClassValue)
						except:
							# GLYPHS 2:
							newInstance.weightClass = weightClassOldName
							if weightClassValue % 100:
								newInstance.customParameters["weightClass"] = weightClassValue

						# style name (with italic) and style linking
						newInstance.name = self.completeStyleName(prefix, self.italicStyleName(styleName))
						styleLinkedName = ""

						if styleName == "Bold":
							newInstance.isBold = True
							styleLinkedName = "Regular"
						if self.pref("italicStyle"):
							newInstance.isItalic = True
							if not styleLinkedName:
								styleLinkedName = styleName
						newInstance.linkStyle = self.completeStyleName(prefix, styleLinkedName)

						# fix style linking to mere "Regular" (should be empty):
						if newInstance.linkStyle == "Regular":
							newInstance.linkStyle = None
					else:
						newInstance.name = "%s%i" % (prefix, thisWeight)
						newInstance.isBold = False

					if theFont:
						if Glyphs.versionNumber >= 3:
							# GLYPHS 3:
							weightID = self.weightID(theFont)
							widthID = self.widthID(theFont)
							if weightID:
								newInstance.setAxisValueValue_forId_(thisWeight, weightID)
							if widthID:
								newInstance.setAxisValueValue_forId_(widthValue, widthID)

							# Axis Location:
							if self.pref("axisLocation") and self.pref("naturalNames"):
								axisLocations = []
								for thisAxis in theFont.axes:
									if thisAxis.name == "Weight":
										if weightClassValue is not None:
											value = weightClassValue
										else:
											value = 400
									elif thisAxis.name == "Width":
										value = widthValue
									else:
										value = 0
									axisLocations.append(axisLocationEntry(thisAxis.name, value))
								if axisLocations:
									newInstance.customParameters[paramName] = tuple(axisLocations)

						else:
							# GLYPHS 2:
							newInstance.weightValue = thisWeight
							newInstance.widthValue = widthValue

						if maciejYesOrNo:
							interpolationY = distribute_maciej(maciejValues[0], maciejValues[1], maciejValues[2], maciejValues[3], float(thisWeight))
							if roundingYesOrNo:
								interpolationY = round(interpolationY)
							newInstance.customParameters["InterpolationWeightY"] = ("%.1f" % interpolationY).replace(".0", "")

						# add the created instance:
						theFont.instances.append(newInstance)
						newInstance.updateInterpolationValues()
					else:
						print("Error: No current font.")

				# set Axis Location for masters if possible:
				if Glyphs.versionNumber >= 3 and theFont and self.pref("naturalNames") and self.pref("axisLocation") and self.pref("axisLocationMaster"):
					for thisMaster in theFont.masters:
						for thisInstance in [i for i in theFont.instances if i.type == 0]:
							if thisMaster.axes == thisInstance.axes:
								thisMaster.customParameters[paramName] = thisInstance.customParameters[paramName]
								break

			self.SavePreferences()

			if not self.pref("keepWindowOpen"):
				self.w.close()
		except Exception as e:
			print(e)
			import traceback
			print(traceback.format_exc())


# ---- Glyphs 4+ particles UI ----

def insertParticlesIntoFont(font, particlesDict):
	"""
	Stub for inserting axis particles into the font.
	particlesDict structure:
	{
	    'elidableNames': ['Regular', 'Normal', 'Roman'],
	    'removeInstances': bool,
	    'removeParticles': bool,
	    'axes': {
	        'wght': {
	            'firstName': 'Hairline',
	            'lastName': 'Black',
	            'algorithm': 'linear',
	            'particles': [
	                {'name': 'Hairline', 'externalValue': 1, 'internalValue': 50},
	                ...
	            ],
	        },
	        'wdth': {
	            'values': [75.0, 100.0, 125.0],
	            'rangeMin': 75.0,
	            'rangeMax': 125.0,
	        },
	    },
	}
	"""
	print("Report for Insert Instances (particles)\n")
	print(f"\t📄 Font: {font.familyName if font else 'None'}")
	print(f"\t☑️  Remove instances: {particlesDict.get('removeInstances')}")
	print(f"\t☑️  Remove particles: {particlesDict.get('removeParticles')}")
	print(f"\t🔠 Elidable names: {', '.join(particlesDict.get('elidableNames', []))}")
	for axisTag, axisData in particlesDict.get("axes", {}).items():
		print(f"\n\t↔️  Axis: {axisTag}")
		if "particles" in axisData:
			for p in axisData["particles"]:
				print(f"\t\t• {p['name']} (external: {p['externalValue']}, internal: {p['internalValue']})")
		else:
			print(f"\t\tValues: {axisData.get('values')}")
			print(f"\t\tRange: {axisData.get('rangeMin')} – {axisData.get('rangeMax')}")


class InstanceMakerV4(mekkaObject):
	"""GUI for inserting axis particles (Glyphs 4+)."""

	defaultElidableNames = "Regular, Normal, Roman"

	prefDict = {
		"removeInstances": False,
		"removeParticles": False,
		"elidableNames": "Regular, Normal, Roman",
	}

	# Width of the left-column labels, sized to fit "Distribution:" at sizeStyle="small"
	_labelW = 82

	def __init__(self):
		thisFont = Glyphs.font

		# Collect font axes
		self.fontAxes = []
		if thisFont and thisFont.axes:
			for axis in thisFont.axes:
				tag = axis.axisTag
				name = axis.name
				safeTag = _safeAttrName(tag)
				self.fontAxes.append({"tag": tag, "safeTag": safeTag, "name": name, "axis": axis})

		# Build instance-level prefDict with dynamic axis entries
		self.prefDict = dict(InstanceMakerV4.prefDict)
		for axisInfo in self.fontAxes:
			tag = axisInfo["tag"]
			safeTag = axisInfo["safeTag"]
			if tag == "wght":
				self.prefDict["wght_firstName"] = 0   # Hairline
				self.prefDict["wght_lastName"] = 9    # Black
				self.prefDict["wght_algorithm"] = 0   # linear
			else:
				self.prefDict[f"{safeTag}_values"] = ""
				self.prefDict[f"{safeTag}_range"] = "min:max"

		inset = 15
		lineHeight = 26
		windowWidth = 390
		# NSTextAlignmentRight = 2
		rightAlign = 2

		# Calculate required window height
		linePos = 12
		linePos += lineHeight  # remove checkboxes row
		linePos += lineHeight  # elidable names row
		linePos += 9           # header divider
		for i, axisInfo in enumerate(self.fontAxes):
			linePos += lineHeight  # section title
			linePos += lineHeight  # first data row (first/last weight OR values)
			linePos += lineHeight  # second data row (distribution OR range)
			if i < len(self.fontAxes) - 1:
				linePos += 9  # divider between sections
		if not self.fontAxes:
			linePos += lineHeight  # "no axes" message
		linePos += 75  # bottom divider + button row + inset

		windowHeight = linePos

		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Insert Instances",
			minSize=(windowWidth, windowHeight),
			maxSize=(windowWidth + 1000, windowHeight),
			autosaveName=self.domain("mainwindow_v4"),
		)

		linePos = 12

		# Row: Remove checkboxes
		self.w.removeInstances = vanilla.CheckBox(
			(inset, linePos, 185, 20),
			"Remove existing instances",
			value=False,
			callback=self.SavePreferences,
			sizeStyle="small",
		)
		self.w.removeInstances.setToolTip("Remove all existing instances from the frontmost font before inserting.")
		self.w.removeParticles = vanilla.CheckBox(
			(inset + 192, linePos, -inset, 20),
			"Remove existing particles",
			value=False,
			callback=self.SavePreferences,
			sizeStyle="small",
		)
		self.w.removeParticles.setToolTip("Remove all existing axis particles from the frontmost font before inserting.")
		linePos += lineHeight

		# Row: Elidable names
		self.w.elidableLabel = vanilla.TextBox(
			(inset, linePos + 2, 102, 14),
			"Elidable names:",
			sizeStyle="small",
		)
		self.w.elidableNames = vanilla.EditText(
			(inset + 103, linePos - 1, -inset - 22, 19),
			self.defaultElidableNames,
			callback=self.SavePreferences,
			sizeStyle="small",
		)
		self.w.elidableNames.setToolTip("Comma-separated style names that are elidable: they can be omitted from composite names, e.g. 'Condensed Regular' becomes 'Condensed'.")
		self.w.elidableNamesReset = UpdateButton(
			(-inset - 18, linePos - 1, -inset, 18),
			callback=self.resetElidableNames,
		)
		self.w.elidableNamesReset.setToolTip(f"Reset to defaults: {self.defaultElidableNames}")
		linePos += lineHeight

		# Divider below header
		self.w.dividerTop = vanilla.HorizontalLine((inset, linePos, -inset, 1))
		linePos += 9

		# Per-axis sections
		labelW = self._labelW  # common left-column label width for consistent input alignment
		inputX = inset + labelW + 2  # x where all left-column inputs start

		if self.fontAxes:
			for i, axisInfo in enumerate(self.fontAxes):
				tag = axisInfo["tag"]
				safeTag = axisInfo["safeTag"]
				name = axisInfo["name"]

				# Section title: "Particles for: wght (Weight)"
				setattr(
					self.w,
					f"sectionTitle_{safeTag}",
					vanilla.TextBox((inset, linePos + 2, -inset, 14), f"Particles for: {tag} ({name})", sizeStyle="small"),
				)
				linePos += lineHeight

				if tag == "wght":
					# "First:" label (right-aligned) + popup
					firstLabel = vanilla.TextBox((inset, linePos + 2, labelW, 14), "First:", sizeStyle="small")
					firstLabel.getNSTextField().setAlignment_(rightAlign)
					setattr(self.w, f"firstWeightLabel_{safeTag}", firstLabel)

					firstPicker = vanilla.PopUpButton(
						(inputX, linePos, 122, 17),
						list(naturalNames),
						callback=self.SavePreferences,
						sizeStyle="small",
					)
					firstPicker.setToolTip("Name of the lightest weight particle to add.")
					setattr(self.w, "wght_firstName", firstPicker)

					# "Last:" label (right-aligned) + popup (same row, Last popup stretches)
					lastLabelX = inputX + 122 + 8
					lastLabel = vanilla.TextBox((lastLabelX, linePos + 2, 44, 14), "Last:", sizeStyle="small")
					lastLabel.getNSTextField().setAlignment_(rightAlign)
					setattr(self.w, f"lastWeightLabel_{safeTag}", lastLabel)

					lastPicker = vanilla.PopUpButton(
						(lastLabelX + 46, linePos, -inset, 17),
						list(naturalNames),
						callback=self.SavePreferences,
						sizeStyle="small",
					)
					lastPicker.setToolTip("Name of the heaviest weight particle to add.")
					setattr(self.w, "wght_lastName", lastPicker)
					linePos += lineHeight

					# "Distribution:" label (right-aligned) + popup
					distLabel = vanilla.TextBox((inset, linePos + 2, labelW, 14), "Distribution:", sizeStyle="small")
					distLabel.getNSTextField().setAlignment_(rightAlign)
					setattr(self.w, f"distributionLabel_{safeTag}", distLabel)

					distPicker = vanilla.PopUpButton(
						(inputX, linePos, 185, 17),
						list(distributionNames),
						callback=self.SavePreferences,
						sizeStyle="small",
					)
					distPicker.setToolTip(distributionExplanation)
					setattr(self.w, "wght_algorithm", distPicker)
					linePos += lineHeight

				else:
					# "Values:" label (right-aligned) + field
					valLabel = vanilla.TextBox((inset, linePos + 2, labelW, 14), "Values:", sizeStyle="small")
					valLabel.getNSTextField().setAlignment_(rightAlign)
					setattr(self.w, f"valuesLabel_{safeTag}", valLabel)

					valField = vanilla.EditText(
						(inputX, linePos - 1, -inset, 19),
						"",
						callback=self.SavePreferences,
						sizeStyle="small",
					)
					valField.setToolTip("Comma-separated axis values to use as particles. They will be distributed linearly across the defined range.")
					setattr(self.w, f"{safeTag}_values", valField)
					linePos += lineHeight

					# "Range:" label (right-aligned) + field
					rangeLabel = vanilla.TextBox((inset, linePos + 2, labelW, 14), "Range:", sizeStyle="small")
					rangeLabel.getNSTextField().setAlignment_(rightAlign)
					setattr(self.w, f"rangeLabel_{safeTag}", rangeLabel)

					rangeField = vanilla.EditText(
						(inputX, linePos - 1, -inset, 19),
						"min:max",
						callback=self.SavePreferences,
						sizeStyle="small",
					)
					rangeField.setToolTip("Distribution range as min:max. Use 'min'/'max' for the axis endpoints, or leave as 'min:max' for the full range. Examples: 'min:100', '200:max', '75:125'.")
					setattr(self.w, f"{safeTag}_range", rangeField)
					linePos += lineHeight

				# Divider between axis sections (not after the last one)
				if i < len(self.fontAxes) - 1:
					setattr(
						self.w,
						f"divider_{safeTag}",
						vanilla.HorizontalLine((inset, linePos, -inset, 1)),
					)
					linePos += 9
		else:
			self.w.noAxesMessage = vanilla.TextBox(
				(inset, linePos + 2, -inset, 14),
				"No axes found in the frontmost font.",
				sizeStyle="small",
			)
			linePos += lineHeight

		# Divider above button bar (10px above button top)
		self.w.dividerBottom = vanilla.HorizontalLine((inset, -47, -inset, 1))

		# Reset at bottom-left, Insert at bottom-right — regular size (22px tall)
		self.w.resetButton = vanilla.Button(
			(inset, -22 - inset, 90, -inset),
			"Reset",
			callback=self.resetAction,
			sizeStyle="regular",
		)
		self.w.resetButton.setToolTip("Reset all form fields to their defaults.")
		self.w.insertButton = vanilla.Button(
			(-80 - inset, -22 - inset, -inset, -inset),
			"Insert",
			callback=self.insertAction,
			sizeStyle="regular",
		)
		self.w.insertButton.setToolTip("Insert axis particles into the frontmost font.")
		self.w.setDefaultButton(self.w.insertButton)

		self.LoadPreferences()
		self.w.open()
		self.w.makeKey()

	def resetElidableNames(self, sender=None):
		self.w.elidableNames.set(self.defaultElidableNames)
		self.SavePreferences()

	def resetAction(self, sender=None):
		self.w.removeInstances.set(False)
		self.w.removeParticles.set(False)
		self.w.elidableNames.set(self.defaultElidableNames)
		for axisInfo in self.fontAxes:
			tag = axisInfo["tag"]
			safeTag = axisInfo["safeTag"]
			if tag == "wght":
				getattr(self.w, "wght_firstName").set(0)  # Hairline
				getattr(self.w, "wght_lastName").set(9)   # Black
				getattr(self.w, "wght_algorithm").set(0)  # linear
			else:
				getattr(self.w, f"{safeTag}_values").set("")
				getattr(self.w, f"{safeTag}_range").set("min:max")
		self.SavePreferences()

	def buildParticlesDict(self):
		thisFont = Glyphs.font
		if not thisFont:
			print("❌ No font open.")
			return None

		elidableNames = [n.strip() for n in self.w.elidableNames.get().split(",") if n.strip()]
		axesData = {}

		for axisInfo in self.fontAxes:
			tag = axisInfo["tag"]
			safeTag = axisInfo["safeTag"]
			axis = axisInfo["axis"]
			axisMin = axis.minimum
			axisMax = axis.maximum

			if tag == "wght":
				firstIndex = getattr(self.w, "wght_firstName").get()
				lastIndex = getattr(self.w, "wght_lastName").get()
				algorithmIndex = getattr(self.w, "wght_algorithm").get()
				algorithmName = distributionNames[algorithmIndex]

				# Ensure correct order
				if firstIndex > lastIndex:
					firstIndex, lastIndex = lastIndex, firstIndex

				selectedNames = list(naturalNames[firstIndex:lastIndex + 1])
				n = len(selectedNames)
				internalValues = applyDistribution(algorithmName, axisMin, axisMax, n)

				particles = [
					{
						"name": name,
						"externalValue": weightClasses[name],
						"internalValue": round(val),
					}
					for name, val in zip(selectedNames, internalValues)
				]

				axesData["wght"] = {
					"firstName": naturalNames[firstIndex],
					"lastName": naturalNames[lastIndex],
					"algorithm": algorithmName,
					"particles": particles,
				}

			else:
				valuesStr = getattr(self.w, f"{safeTag}_values").get().strip()
				rangeStr = getattr(self.w, f"{safeTag}_range").get().strip()

				values = []
				for v in valuesStr.split(","):
					v = v.strip()
					if v:
						try:
							values.append(float(v))
						except ValueError:
							pass

				rangeMin = axisMin
				rangeMax = axisMax
				if ":" in rangeStr:
					minPart, maxPart = rangeStr.split(":", 1)
					minPart = minPart.strip()
					maxPart = maxPart.strip()
					if minPart and minPart.lower() != "min":
						try:
							rangeMin = float(minPart)
						except ValueError:
							pass
					if maxPart and maxPart.lower() != "max":
						try:
							rangeMax = float(maxPart)
						except ValueError:
							pass

				axesData[tag] = {
					"values": values,
					"rangeMin": rangeMin,
					"rangeMax": rangeMax,
				}

		return {
			"elidableNames": elidableNames,
			"removeInstances": bool(self.w.removeInstances.get()),
			"removeParticles": bool(self.w.removeParticles.get()),
			"axes": axesData,
		}

	def insertAction(self, sender=None):
		thisFont = Glyphs.font
		if not thisFont:
			print("❌ Insert Instances: no font open.")
			return
		particlesDict = self.buildParticlesDict()
		if particlesDict is None:
			return
		self.SavePreferences()
		Glyphs.clearLog()
		insertParticlesIntoFont(thisFont, particlesDict)
		Glyphs.showNotification("Insert Instances", "Done. Details in Macro Window.")


if Glyphs.versionNumber >= 4:
	InstanceMakerV4()
else:
	InstanceMaker()
