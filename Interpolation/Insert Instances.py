# MenuTitle: Insert Instances
__doc__ = """
Inserts instances, based on the Luc(as), Pablo, Abraham, Schneider and Maciej algorithms.
In Glyphs 4+, presents a redesigned UI for inserting axis particles.
"""

import vanilla
from mekkablue import mekkaObject, UpdateButton, SteppingEditText, decimalFormatter, makeWindowResizable
from GlyphsApp import Glyphs, GSInstance, INSTANCETYPESINGLE
from AppKit import NSFont, NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityDefaultLow, NSLayoutPriorityRequired, NSLayoutPriorityWindowSizeStayPut, NSTextAlignmentRight
from Foundation import NSDictionary, NSMutableArray, NSMutableDictionary

if Glyphs.versionNumber >= 4:
	from GlyphsApp import GSNameParticle

INSTANCETYPEPARTICLE = 4  # GSInstance.type for axis particle instances (Glyphs 4+)


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
		"numberOfInstances": 3,  # index of "6" in the popup (3 to 11)
		"prefix": "",
		"master1": 1,  # self.MasterList(1),
		"master2": -1,  # self.MasterList(-1),
		"width": 100,
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
		windowWidth = 400
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Insert weight instances",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and height
		)

		# UI elements:
		inset = 15

		self.w.text_1 = vanilla.TextBox("auto", "Insert", sizeStyle='small')
		self.w.numberOfInstances = vanilla.PopUpButton("auto", [str(x) for x in range(3, 12)], callback=self.UpdateSample, sizeStyle='small')
		self.w.numberOfInstances.setToolTip("Choose how many weights you want to add.")
		self.w.text_2 = vanilla.TextBox("auto", "weights with prefix", sizeStyle='small')
		self.w.prefix = vanilla.EditText("auto", "A-", callback=self.UpdateSample, sizeStyle='small')
		self.w.prefix.setToolTip("Choose text that is added at the beginning of each instance, e.g., 'Condensed'.")

		self.w.text_3 = vanilla.TextBox("auto", "from:", sizeStyle='small')
		self.w.master1 = vanilla.ComboBox("auto", self.MasterList(1), callback=self.UpdateSample, sizeStyle='small')
		self.w.master1.setToolTip("Weight value for the first instance being added, typically the stem width of your lightest weight.")
		self.w.text_4 = vanilla.TextBox("auto", "through:", sizeStyle='small')
		self.w.master2 = vanilla.ComboBox("auto", self.MasterList(-1), callback=self.UpdateSample, sizeStyle='small')
		self.w.master2.setToolTip("Weight value for the last instance being added, typically the stem width of your boldest weight.")
		self.w.text_5 = vanilla.TextBox("auto", "at width:", sizeStyle='small')
		widthFormatter = decimalFormatter(1)
		self.w.width = SteppingEditText("auto", "100", callback=self.UpdateSample, sizeStyle='small', formatter=widthFormatter)
		self.w.width.setToolTip("The Width value for the instances being added. Default is 100. Adapt accordingly if you are adding condensed or extended instances.")

		self.w.text_6 = vanilla.TextBox("auto", "using", sizeStyle='small')
		self.w.algorithm = vanilla.PopUpButton("auto", distributionNames, callback=self.UpdateSample, sizeStyle='small')
		self.w.algorithm.setToolTip(distributionExplanation)
		self.w.text_7 = vanilla.TextBox("auto", "distribution.", sizeStyle='small')
		self.w.help_instances = vanilla.HelpButton("auto", callback=self.openURL)
		self.w.help_instances.setToolTip("Opens a tutorial about setting up instances in a web browser. Requires an internet connection.")

		self.w.existingInstances = vanilla.VerticalRadioGroup("auto", ("Leave existing instances as they are", "Deactivate existing instances", "Delete existing instances"), callback=self.SavePreferences, sizeStyle='small')
		self.w.existingInstances.setToolTip("What happens to the instances that already exist in the font: keep, deactivate or delete them.")
		self.w.existingInstances.set(0)

		self.w.naturalNames = vanilla.CheckBox("auto", "Use 'natural' weight names, starting at:", value=False, callback=self.UpdateSample, sizeStyle='small')
		self.w.naturalNames.setToolTip("Prefill with standard names and style linking. If turned off, will use the Weight number as instance name.")
		self.w.firstName = vanilla.PopUpButton("auto", naturalNames, callback=self.UpdateSample, sizeStyle='small')
		self.w.firstName.setToolTip("If you use natural weight names, choose here the name of your lightest weight.")

		hasAxisLocation = Glyphs.versionNumber >= 3
		if hasAxisLocation:
			self.w.axisLocation = vanilla.CheckBox("auto", "Set Axis Location for each instance", value=True, callback=self.SavePreferences, sizeStyle='small')
			self.w.axisLocationMaster = vanilla.CheckBox("auto", "and master", value=True, callback=self.SavePreferences, sizeStyle='small')
			self.w.axisLocation.setToolTip("If enabled, will add an Axis Location parameter with the proper usWeightClass value in Font Info → Exports.\n\nHINT: Do not forget to set Axis Location parameters for each master in Font Info → Masters, and remove the Axis Mappings parameter in Font Info → Font if you have one.")
			self.w.axisLocationMaster.setToolTip("If enabled, will attempt to set Axis Locations for masters as well. Only works if there is an instance that matches the respective master.")

		self.w.italicStyle = vanilla.CheckBox("auto", "Italic suffixes and style linking", value=False, callback=self.UpdateSample, sizeStyle='small')
		self.w.italicStyle.setToolTip("If enabled, will add the word 'Italic' to all instances, and also add italic style linking.")

		self.w.maciej = vanilla.CheckBox("auto", "Maciej y distribution from:", value=False, callback=self.UpdateSample, sizeStyle='small')
		self.w.maciej.setToolTip("An algorithm proposed by Maciej Ratajski, which introduces slightly different interpolation for y coordinates. Will add interpolationWeightY parameters to the instances. If these value differ greatly from the weight interpolation values, interpolation of your diagonals may suffer.")
		self.w.maciej_light = vanilla.ComboBox("auto", self.MasterList(1), callback=self.UpdateSample, sizeStyle='small')
		self.w.maciej_light.setToolTip("Horizontal stem width of the lightest master, for interpolating contrast with the Maciej distribution.")
		self.w.text_maciej_1 = vanilla.TextBox("auto", "through:", sizeStyle='small')
		self.w.maciej_bold = vanilla.ComboBox("auto", self.MasterList(-1), callback=self.UpdateSample, sizeStyle='small')
		tooltipText = "Horizontal stem width of the boldest master, for interpolating contrast with the Maciej distribution."
		self.w.text_maciej_1.setToolTip(tooltipText)
		self.w.maciej_bold.setToolTip(tooltipText)

		self.w.text_maciej_2 = vanilla.TextBox("auto", "Provide horizontal stem widths in extreme masters to interpolate contrast rather than stems.", sizeStyle='small', selectable=True)
		self.w.help_maciej = vanilla.HelpButton("auto", callback=self.openURL)
		self.w.help_maciej.setToolTip("Will open a website with a detailed description of the Maciej algorithm. Requires an internet connection.")

		self.w.shouldRound = vanilla.CheckBox("auto", "Round all interpolation values", value=True, callback=self.UpdateSample, sizeStyle='small')
		self.w.shouldRound.setToolTip("If enabled, will round all calculated weight values to integers. Usually a good idea.")

		self.w.keepWindowOpen = vanilla.CheckBox("auto", "Keep window open", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.keepWindowOpen.setToolTip("If checked, will not close this window after applying the distribution.")

		# the sample takes the leftover height if the user enlarges the window:
		self.w.sample = vanilla.TextEditor("auto", "", readOnly=True)
		self.w.sample.setToolTip("Preview of the instances that will be inserted. Read-only.")
		self.w.sample.getNSTextView().setFont_(NSFont.systemFontOfSize_(NSFont.smallSystemFontSize()))

		# buttons:
		self.w.createButton = vanilla.Button("auto", "Insert", callback=self.CreateInstances)
		self.w.createButton.setToolTip("Inserts the instances into the frontmost font.")
		self.w.setDefaultButton(self.w.createButton)

		# checkboxes stretch vertically by default; with everything hugging, the window
		# ends up exactly as tall as the content, except for the sample box, which may grow:
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)
		self.w.sample.getNSScrollView().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationVertical)

		# the explanation wraps, so it must not demand one long line:
		self.w.text_maciej_2.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		# labels in front of fields are right-aligned and share one width, so the fields line up:
		labelNames = ("text_1", "text_3", "text_6")
		for labelName in labelNames:
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)
		widthRules = [{"view1": getattr(self.w, labelName), "attribute1": "width", "view2": self.w.text_1, "attribute2": "width"} for labelName in labelNames if labelName != "text_1"]

		# the checkbox hugs its text, the popup behind it stretches:
		self.w.naturalNames.getNSButton().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
		self.w.firstName.getNSPopUpButton().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		rules = [
			"H:|-inset-[text_1]-gap-[numberOfInstances]-gap-[text_2]-gap-[prefix]-inset-|",
			"H:|-inset-[text_3]-gap-[master1(62)]-gap-[text_4]-gap-[master2(62)]-gap-[text_5]-gap-[width(>=50)]-inset-|",
			"H:|-inset-[text_6]-gap-[algorithm]-gap-[text_7]-(>=gap)-[help_instances]-inset-|",
			"H:|-indent-[existingInstances]-(>=inset)-|",
			"H:|-inset-[naturalNames]-gap-[firstName]-inset-|",
			"H:|-indent-[italicStyle]-(>=inset)-|",
			"H:|-inset-[maciej]-gap-[maciej_light(55)]-gap-[text_maciej_1]-gap-[maciej_bold(55)]-(>=inset)-|",
			"H:|-indent-[text_maciej_2]-gap-[help_maciej]-inset-|",
			"H:|-inset-[shouldRound]-gap-[keepWindowOpen]-(>=inset)-|",
			"H:|-inset-[sample]-inset-|",
			"H:|-(>=inset)-[createButton(>=70)]-inset-|",
			# one baseline per row:
			{"view1": self.w.text_1, "attribute1": "centerY", "view2": self.w.prefix, "attribute2": "centerY"},
			{"view1": self.w.numberOfInstances, "attribute1": "centerY", "view2": self.w.prefix, "attribute2": "centerY"},
			{"view1": self.w.text_2, "attribute1": "centerY", "view2": self.w.prefix, "attribute2": "centerY"},
			{"view1": self.w.text_3, "attribute1": "centerY", "view2": self.w.master1, "attribute2": "centerY"},
			{"view1": self.w.text_4, "attribute1": "centerY", "view2": self.w.master1, "attribute2": "centerY"},
			{"view1": self.w.master2, "attribute1": "centerY", "view2": self.w.master1, "attribute2": "centerY"},
			{"view1": self.w.text_5, "attribute1": "centerY", "view2": self.w.master1, "attribute2": "centerY"},
			{"view1": self.w.width, "attribute1": "centerY", "view2": self.w.master1, "attribute2": "centerY"},
			{"view1": self.w.text_6, "attribute1": "centerY", "view2": self.w.algorithm, "attribute2": "centerY"},
			{"view1": self.w.text_7, "attribute1": "centerY", "view2": self.w.algorithm, "attribute2": "centerY"},
			{"view1": self.w.help_instances, "attribute1": "centerY", "view2": self.w.algorithm, "attribute2": "centerY"},
			{"view1": self.w.firstName, "attribute1": "centerY", "view2": self.w.naturalNames, "attribute2": "centerY"},
			{"view1": self.w.maciej_light, "attribute1": "centerY", "view2": self.w.maciej, "attribute2": "centerY"},
			{"view1": self.w.text_maciej_1, "attribute1": "centerY", "view2": self.w.maciej, "attribute2": "centerY"},
			{"view1": self.w.maciej_bold, "attribute1": "centerY", "view2": self.w.maciej, "attribute2": "centerY"},
			{"view1": self.w.help_maciej, "attribute1": "centerY", "view2": self.w.text_maciej_2, "attribute2": "centerY"},
			{"view1": self.w.keepWindowOpen, "attribute1": "centerY", "view2": self.w.shouldRound, "attribute2": "centerY"},
			# the first popup and the first combo box are equally wide:
			{"view1": self.w.numberOfInstances, "attribute1": "width", "view2": self.w.master1, "attribute2": "width"},
		] + widthRules
		stack = "[naturalNames]-stackRow-"
		if hasAxisLocation:
			rules += [
				"H:|-indent-[axisLocation]-gap-[axisLocationMaster]-(>=inset)-|",
				{"view1": self.w.axisLocationMaster, "attribute1": "centerY", "view2": self.w.axisLocation, "attribute2": "centerY"},
			]
			stack += "[axisLocation]-stackRow-"
		rules.append(f"V:|-inset-[prefix]-row-[master1]-row-[algorithm]-sectionGap-[existingInstances(radioHeight)]-sectionGap-{stack}[italicStyle]-stackRow-[maciej]-stackRow-[text_maciej_2(28)]-stackRow-[shouldRound]-sectionGap-[sample(>=100)]-inset-[createButton]-inset-|")

		self.w.addAutoPosSizeRules(
			rules,
			metrics={"inset": inset, "indent": inset + 20, "gap": 8, "row": 8, "stackRow": 8, "sectionGap": 10, "radioHeight": self.w.existingInstances.getFittingHeight()},
		)

		# resizable vertically only, so the sample can grow:
		makeWindowResizable(self.w, vertical=True, horizontal=False)

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

			lastValue = float(distributedValues[-1])
			firstValue = float(distributedValues[0])
			if self.w.algorithm.getItem() == "Luc(as)" and firstValue != 0:
				growth = (lastValue / firstValue)**(1.0 / (n - 1))
				sampleText += ",%s growth: %.1f%%" % (
					" average" if self.pref("shouldRound") else "",
					(growth - 1) * 100,
				)

			if self.pref("maciej"):
				maciejValues = self.MaciejValues()
				if maciejValues:
					maciejList = [str(round(distribute_maciej(maciejValues[0], maciejValues[1], maciejValues[2], maciejValues[3], w), rounding)) for w in distributedValues]
					sampleText += "\n\nWill add interpolationWeightY parameters to instances: %s" % (", ".join(maciejList) + ".")

			self.w.sample.set(sampleText)
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
			if theFont is None:
				print("❌ Insert Instances: no font open.")
				return
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
								axisLocation = thisInstance.customParameters[paramName]
								if axisLocation:
									# skip instances without Axis Location, a None value would end up as NSNull and break saving
									thisMaster.customParameters[paramName] = axisLocation
									break

			self.SavePreferences()

			if not self.pref("keepWindowOpen"):
				self.w.close()
		except Exception as e:
			print(e)
			import traceback
			print(traceback.format_exc())


# ---- Glyphs 4+ particles UI ----

# usWidthClass and its approximate width in percent of normal, from the OpenType spec (OS/2 table, 5 is normal):
# https://learn.microsoft.com/en-us/typography/opentype/spec/os2#uswidthclass
widthClassPercentages = {
	1: 50,  # Ultra-condensed
	2: 62.5,  # Extra-condensed
	3: 75,  # Condensed
	4: 87.5,  # Semi-condensed
	5: 100,  # Medium (normal)
	6: 112.5,  # Semi-expanded
	7: 125,  # Expanded
	8: 150,  # Extra-expanded
	9: 200,  # Ultra-expanded
}

# GSNameParticle attributes (isElidable, widthClass) are available since this Glyphs build:
BUILD_WITH_PARTICLE_ATTRIBUTES = 4204


def widthClassForPercentage(percent):
	"""Returns the usWidthClass (1 to 9) whose width in percent of normal is closest to this value."""
	return min(widthClassPercentages, key=lambda widthClass: (abs(widthClassPercentages[widthClass] - percent), widthClass))


def externalAxisValue(font, axisId, internalValue):
	"""
	Returns the user-space (external) value on this axis for a design-space (internal) value,
	interpolated between the master coordinates, which carry both. Without a mapping, they are the same.
	"""
	pairs = sorted({(float(master.internalAxesValues[axisId]), float(master.externalAxesValues[axisId])) for master in font.masters})
	if len(pairs) < 2:
		return float(internalValue)
	# the segment between two masters that contains the value, or the first or last segment to extrapolate:
	index = 1
	while index < len(pairs) - 1 and internalValue > pairs[index][0]:
		index += 1
	(internal1, external1), (internal2, external2) = pairs[index - 1], pairs[index]
	return external1 + (float(internalValue) - internal1) * (external2 - external1) / (internal2 - internal1)


def defaultNamesForAxis(axisTag):
	"""The particle names an axis starts with, and is reset to."""
	return "Roman, Italic" if axisTag == "ital" else ""


uprightNames = ("roman", "regular", "normal")
italicNames = ("italic", "oblique")


def styleLinksForAxis(font, axisId, axisTag, particleInfos):
	"""
	Returns a dictionary of particle name: (attribute, linked particle name) for style linking on one axis:
	• wght: the Bold particle (or external value 700) is bold, and links to Regular, Normal or Roman (or external value 400),
	• ital and slnt: the Italic or Oblique particle (or ital=1, or the most negative slnt) is italic,
	  and links to Roman, Regular or Normal (or ital=0 or slnt=0).
	"""
	if axisTag not in ("wght", "ital", "slnt"):
		return {}

	# the values the styles are recognized by are the user-space (external) values:
	values = []
	for info in particleInfos:
		externalValue = info.get("externalValue")
		values.append(float(externalValue) if externalValue is not None else externalAxisValue(font, axisId, info["internalValue"]))
	names = [info["name"] for info in particleInfos]
	isName = lambda index, candidates: names[index].strip().lower() in candidates

	if axisTag == "wght":
		styleIndexes = [i for i in range(len(names)) if isName(i, ("bold", )) or abs(values[i] - 700) < 0.001]
		targetIndexes = [i for i in range(len(names)) if abs(values[i] - 400) < 0.001] or [i for i in range(len(names)) if isName(i, uprightNames)]
		attribute = "isBold"
	else:
		mostNegative = min(values) if values else 0
		styleIndexes = [
			i for i in range(len(names))
			if isName(i, italicNames) or (axisTag == "ital" and abs(values[i] - 1) < 0.001) or (axisTag == "slnt" and mostNegative < 0 and values[i] == mostNegative)
		]
		targetIndexes = [i for i in range(len(names)) if abs(values[i]) < 0.001] or [i for i in range(len(names)) if isName(i, uprightNames)]
		attribute = "isItalic"

	targetIndexes = [i for i in targetIndexes if i not in styleIndexes]
	if not styleIndexes or not targetIndexes:
		return {}
	targetName = names[targetIndexes[0]]
	return {names[i]: (attribute, targetName) for i in styleIndexes}


def buildNameParticle(name, internalValue, externalValue):
	"""
	Returns a GSNameParticle with the supplied name and axis values.
	"""
	particle = GSNameParticle.alloc().init()
	particle.name = name
	particle.internal = float(internalValue)
	if externalValue is None or float(externalValue) == float(internalValue):
		# no mapping necessary if both values are the same:
		particle.external = None
	else:
		particle.external = float(externalValue)
	return particle


def insertParticlesIntoFont(font, particlesDict):
	"""
	Insert axis particles into the font using GSNameParticle (Glyphs 4+).
	particlesDict structure:
	{
	    'elidableNames': ['Regular', 'Normal', 'Roman'],
	    'removeInstances': bool,
	    'removeParticles': bool,
	    'axes': {
	        'wght': {
	            'particles': [{'name': 'Hairline', 'externalValue': 1, 'internalValue': 50}, ...],
	        },
	        'wdth': {
	            'particles': [{'name': 'Narrow', 'internalValue': 25.0}, ...],
	        },
	    },
	}
	"""
	print("Report for Insert Instances (particles)\n")
	print(f"\t📄 Font: {font.familyName}")

	removeInstances = particlesDict.get("removeInstances", False)
	removeParticles = particlesDict.get("removeParticles", False)
	elidableNames = particlesDict.get("elidableNames", [])
	axesData = particlesDict.get("axes", {})
	hasAttributes = Glyphs.buildNumber >= BUILD_WITH_PARTICLE_ATTRIBUTES

	if removeInstances:
		count = 0
		for i, instance in reversed(list(enumerate(font.instances))):
			if instance.type == INSTANCETYPESINGLE:
				del font.instances[i]
				count += 1
		print(f"\t🗑️ Removed {count} existing instance(s).")

	if removeParticles:
		count = 0
		for i, instance in reversed(list(enumerate(font.instances))):
			if instance.type == INSTANCETYPEPARTICLE:
				del font.instances[i]
				count += 1
		print(f"\t🗑️ Removed {count} existing particle instance(s).")

	# Build axis tag → axisId lookup:
	axisIdForTag = {axis.axisTag: axis.axisId for axis in font.axes}

	# Always add a new set of particles. Particles that were in the font before are
	# left alone, unless the user asked for them to be removed (see removeParticles above):
	particleInstance = GSInstance()
	particleInstance.setType_(INSTANCETYPEPARTICLE)
	font.instances.append(particleInstance)
	print("\t✅ Added new set of particles.")

	allParticles = NSMutableDictionary.dictionary()

	# Build name particles for each axis:
	for axisTag, axisData in axesData.items():
		axisId = axisIdForTag.get(axisTag)
		if axisId is None:
			print(f"\t⚠️ No axisId found for axis tag '{axisTag}', skipping.")
			continue

		particles = axisData.get("particles", ())
		print(f"\n\t↔️ Axis: {axisTag}")
		if not particles:
			print("\t\t⚠️ No particles defined, skipping.")
			continue

		axisParticles = NSMutableArray.array()
		styleLinks = styleLinksForAxis(font, axisId, axisTag, particles) if hasAttributes else {}
		for particleInfo in particles:
			name = particleInfo["name"]
			internalValue = particleInfo["internalValue"]
			# stays None if the axis has no separate external coordinate:
			externalValue = particleInfo.get("externalValue")
			particle = buildNameParticle(name, internalValue, externalValue)
			axisParticles.addObject_(particle)
			if externalValue is None or float(externalValue) == float(internalValue):
				report = f"\t\t✅ {name} ({internalValue})"
			else:
				report = f"\t\t✅ {name} ({internalValue}>{externalValue})"

			if hasAttributes:
				if name in elidableNames:
					particle.setAttribute_forKey_(1, "isElidable")
					report += ", elidable"
				if name in styleLinks:
					# style linking: bold links to regular, italic to roman
					attribute, linkedName = styleLinks[name]
					particle.setAttribute_forKey_(1, attribute)
					particle.setAttribute_forKey_(linkedName, "linkStyle")
					report += f", {'bold' if attribute == 'isBold' else 'italic'} (linked to {linkedName})"
				if axisTag == "wdth":
					# the width class relates to the width in percent of normal, i.e., the external value:
					percent = float(externalValue) if externalValue is not None else externalAxisValue(font, axisId, internalValue)
					widthClass = widthClassForPercentage(percent)
					particle.setAttribute_forKey_(widthClass, "widthClass")
					report += f", width class {widthClass}"
			print(report)

		# adds the particles of this axis to the new set:
		allParticles.setObject_forKey_(axisParticles, axisId)

	particleInstance.setNameParticles_(allParticles)

	if not hasAttributes:
		print(f"\n\t⚠️ Elidable particles, width classes and style linking need Glyphs build {BUILD_WITH_PARTICLE_ATTRIBUTES} or later (this is {Glyphs.buildNumber}), so they were not set.")


class InstanceMakerV4(mekkaObject):
	"""GUI for inserting axis particles (Glyphs 4+)."""

	defaultElidableNames = "Regular, Normal, Roman"

	prefDict = {
		"removeInstances": False,
		"removeParticles": False,
		"elidableNames": "Regular, Normal, Roman",
	}

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
				self.prefDict[f"{safeTag}_values"] = defaultNamesForAxis(tag)
				self.prefDict[f"{safeTag}_range"] = "min:max"

		inset = 15
		windowWidth = 390
		windowHeight = 1  # Auto Layout grows the window to the height the content needs

		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Insert Instances",
			autosaveName=self.domain("mainwindow_v4"),  # stores last window position
		)

		# Row: Remove checkboxes
		self.w.removeInstances = vanilla.CheckBox("auto", "Remove existing instances", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.removeInstances.setToolTip("Remove all existing instances from the frontmost font before inserting.")
		self.w.removeParticles = vanilla.CheckBox("auto", "Remove existing particles", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.removeParticles.setToolTip("Remove all existing axis particles from the frontmost font before inserting. If off, the new particles will be added as an additional set, and existing particles will stay as they are.")

		# Row: Elidable names
		self.w.elidableLabel = vanilla.TextBox("auto", "Elidable names:", sizeStyle="small")
		self.w.elidableNames = vanilla.EditText("auto", self.defaultElidableNames, callback=self.SavePreferences, sizeStyle="small")
		tooltipText = "Comma-separated style names that are elidable: they can be omitted from composite names, e.g. 'Condensed Regular' becomes 'Condensed'. Typical elidable names are ‘Normal’ (wdth), ‘Roman’ (ital) or ‘Regular’ (wght and all other axes)."
		self.w.elidableLabel.setToolTip(tooltipText)
		self.w.elidableNames.setToolTip(tooltipText)
		self.w.elidableNamesReset = UpdateButton("auto", callback=self.resetElidableNames)
		self.w.elidableNamesReset.setToolTip(f"Reset to defaults: {self.defaultElidableNames}")

		# Divider below header
		self.w.dividerTop = vanilla.HorizontalLine("auto")

		rules = [
			"H:|-inset-[removeInstances]-gap-[removeParticles]-(>=inset)-|",
			"H:|-inset-[elidableLabel]-gap-[elidableNames]-gap-[elidableNamesReset]-inset-|",
			"H:|-inset-[dividerTop]-inset-|",
			{"view1": self.w.removeParticles, "attribute1": "centerY", "view2": self.w.removeInstances, "attribute2": "centerY"},
			{"view1": self.w.elidableLabel, "attribute1": "centerY", "view2": self.w.elidableNames, "attribute2": "centerY"},
			{"view1": self.w.elidableNamesReset, "attribute1": "centerY", "view2": self.w.elidableNames, "attribute2": "centerY"},
		]
		verticalChain = "V:|-inset-[removeInstances]-stackRow-[elidableNames]-sectionGap-[dividerTop(1)]"
		labelNames = ["elidableLabel"]  # right-aligned, all as wide as the first one, so the fields line up

		# Per-axis sections
		if self.fontAxes:
			for i, axisInfo in enumerate(self.fontAxes):
				tag = axisInfo["tag"]
				safeTag = axisInfo["safeTag"]
				name = axisInfo["name"]

				# Section title: "Particles for: wght (Weight)"
				titleName = f"sectionTitle_{safeTag}"
				setattr(self.w, titleName, vanilla.TextBox("auto", f"Particles for: {tag} ({name})", sizeStyle="small"))
				rules.append(f"H:|-inset-[{titleName}]-(>=inset)-|")
				verticalChain += f"-sectionGap-[{titleName}]"

				if tag == "wght":
					# "First:" label + popup
					setattr(self.w, f"firstWeightLabel_{safeTag}", vanilla.TextBox("auto", "First:", sizeStyle="small"))
					firstPicker = vanilla.PopUpButton("auto", list(naturalNames), callback=self.SavePreferences, sizeStyle="small")
					firstPicker.setToolTip("Name of the lightest weight particle to add.")
					setattr(self.w, "wght_firstName", firstPicker)

					# "Last:" label + popup (same row)
					setattr(self.w, f"lastWeightLabel_{safeTag}", vanilla.TextBox("auto", "Last:", sizeStyle="small"))
					lastPicker = vanilla.PopUpButton("auto", list(naturalNames), callback=self.SavePreferences, sizeStyle="small")
					lastPicker.setToolTip("Name of the heaviest weight particle to add.")
					setattr(self.w, "wght_lastName", lastPicker)

					# "Distribution:" label + popup
					setattr(self.w, f"distributionLabel_{safeTag}", vanilla.TextBox("auto", "Distribution:", sizeStyle="small"))
					distPicker = vanilla.PopUpButton("auto", list(distributionNames), callback=self.SavePreferences, sizeStyle="small")
					distPicker.setToolTip(distributionExplanation)
					setattr(self.w, "wght_algorithm", distPicker)

					# number of weight particles that will be inserted:
					self.w.wght_particleCount = vanilla.TextBox("auto", "", sizeStyle="small")
					self.w.wght_particleCount.setToolTip("Number of weight particles that will be inserted, from First through Last.")

					labelNames += [f"firstWeightLabel_{safeTag}", f"distributionLabel_{safeTag}"]
					rules += [
						f"H:|-inset-[firstWeightLabel_{safeTag}]-gap-[wght_firstName(>=110)]-gap-[lastWeightLabel_{safeTag}]-gap-[wght_lastName]-inset-|",
						f"H:|-inset-[distributionLabel_{safeTag}]-gap-[wght_algorithm]-gap-[wght_particleCount]-(>=inset)-|",
						{"view1": getattr(self.w, f"firstWeightLabel_{safeTag}"), "attribute1": "centerY", "view2": firstPicker, "attribute2": "centerY"},
						{"view1": getattr(self.w, f"lastWeightLabel_{safeTag}"), "attribute1": "centerY", "view2": firstPicker, "attribute2": "centerY"},
						{"view1": lastPicker, "attribute1": "centerY", "view2": firstPicker, "attribute2": "centerY"},
						{"view1": getattr(self.w, f"distributionLabel_{safeTag}"), "attribute1": "centerY", "view2": distPicker, "attribute2": "centerY"},
						{"view1": self.w.wght_particleCount, "attribute1": "centerY", "view2": distPicker, "attribute2": "centerY"},
						# the three popups are equally wide:
						{"view1": lastPicker, "attribute1": "width", "view2": firstPicker, "attribute2": "width"},
						{"view1": distPicker, "attribute1": "width", "view2": firstPicker, "attribute2": "width"},
					]
					verticalChain += "-row-[wght_firstName]-row-[wght_algorithm]"

				else:
					# "Names:" label + field (the pref and attribute names keep saying values)
					valuesLabelName = f"valuesLabel_{safeTag}"
					setattr(self.w, valuesLabelName, vanilla.TextBox("auto", "Names:", sizeStyle="small"))
					valField = vanilla.EditText("auto", defaultNamesForAxis(tag), callback=self.SavePreferences, sizeStyle="small")
					valField.setToolTip("Comma-separated names of the particles. They will be distributed linearly across the defined range.")
					setattr(self.w, f"{safeTag}_values", valField)

					# "Range:" label + field
					rangeLabelName = f"rangeLabel_{safeTag}"
					setattr(self.w, rangeLabelName, vanilla.TextBox("auto", "Range:", sizeStyle="small"))
					rangeField = vanilla.EditText("auto", "min:max", callback=self.SavePreferences, sizeStyle="small")
					rangeField.setToolTip("Distribution range as min:max. Use 'min'/'max' for the axis endpoints, or leave as 'min:max' for the full range. Examples: 'min:100', '200:max', '75:125'.")
					setattr(self.w, f"{safeTag}_range", rangeField)

					labelNames += [valuesLabelName, rangeLabelName]
					rules += [
						f"H:|-inset-[{valuesLabelName}]-gap-[{safeTag}_values]-inset-|",
						f"H:|-inset-[{rangeLabelName}]-gap-[{safeTag}_range]-inset-|",
						{"view1": getattr(self.w, valuesLabelName), "attribute1": "centerY", "view2": valField, "attribute2": "centerY"},
						{"view1": getattr(self.w, rangeLabelName), "attribute1": "centerY", "view2": rangeField, "attribute2": "centerY"},
					]
					verticalChain += f"-row-[{safeTag}_values]-row-[{safeTag}_range]"

				# Divider between axis sections (not after the last one)
				if i < len(self.fontAxes) - 1:
					dividerName = f"divider_{safeTag}"
					setattr(self.w, dividerName, vanilla.HorizontalLine("auto"))
					rules.append(f"H:|-inset-[{dividerName}]-inset-|")
					verticalChain += f"-sectionGap-[{dividerName}(1)]"
		else:
			self.w.noAxesMessage = vanilla.TextBox("auto", "No axes found in the frontmost font.", sizeStyle="small")
			rules.append("H:|-inset-[noAxesMessage]-(>=inset)-|")
			verticalChain += "-sectionGap-[noAxesMessage]"

		# Divider above button bar
		self.w.dividerBottom = vanilla.HorizontalLine("auto")

		# Reset at bottom-left, Insert at bottom-right
		self.w.resetButton = vanilla.Button("auto", "Reset", callback=self.resetAction)
		self.w.resetButton.setToolTip("Reset all form fields to their defaults.")
		self.w.insertButton = vanilla.Button("auto", "Insert", callback=self.insertAction)
		self.w.insertButton.setToolTip("Insert axis particles into the frontmost font.")
		self.w.setDefaultButton(self.w.insertButton)

		verticalChain += "-sectionGap-[dividerBottom(1)]-inset-[insertButton]-inset-|"
		rules += [
			"H:|-inset-[dividerBottom]-inset-|",
			"H:|-inset-[resetButton(>=70)]-(>=gap)-[insertButton(>=70)]-inset-|",
			verticalChain,
			"V:[resetButton]-inset-|",
		]

		# checkboxes stretch vertically by default; with everything hugging, the window
		# ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# labels are right-aligned and share one width, so the fields line up:
		for labelName in labelNames:
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)
		rules += [{"view1": getattr(self.w, labelName), "attribute1": "width", "view2": self.w.elidableLabel, "attribute2": "width"} for labelName in labelNames[1:]]

		self.w.addAutoPosSizeRules(rules, metrics={"inset": inset, "gap": 8, "row": 8, "stackRow": 8, "sectionGap": 10})

		self.LoadPreferences()
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		if hasattr(self.w, "wght_particleCount"):
			firstIndex = self.w.wght_firstName.get()
			lastIndex = self.w.wght_lastName.get()

			# Last must not come before First:
			if lastIndex < firstIndex:
				lastIndex = firstIndex
				self.w.wght_lastName.set(lastIndex)
				self.setPref("wght_lastName", lastIndex)

			# grey out the entries of Last that precede First:
			lastMenu = self.w.wght_lastName.getNSPopUpButton().menu()
			lastMenu.setAutoenablesItems_(False)
			for index in range(lastMenu.numberOfItems()):
				lastMenu.itemAtIndex_(index).setEnabled_(index >= firstIndex)

			count = lastIndex - firstIndex + 1
			self.w.wght_particleCount.set(f"{count} particle{'' if count == 1 else 's'}")

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
				getattr(self.w, f"{safeTag}_values").set(defaultNamesForAxis(tag))
				getattr(self.w, f"{safeTag}_range").set("min:max")
		self.SavePreferences()

	def _axisRange(self, axisInfo, thisFont):
		"""Return (min, max) of an axis, i.e., the spread of the master coordinates on that axis."""
		axisId = axisInfo["axis"].axisId
		values = [float(master.internalAxesValues[axisId]) for master in thisFont.masters]
		return min(values), max(values)

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
			axisMin, axisMax = self._axisRange(axisInfo, thisFont)

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

				# Values are particle names (strings), not numbers
				names = [v.strip() for v in valuesStr.split(",") if v.strip()]

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

				# Distribute names linearly across the range
				internalVals = applyDistribution("linear", rangeMin, rangeMax, len(names))
				particles = [
					{"name": name, "internalValue": round(iv, 2)}
					for name, iv in zip(names, internalVals)
				]

				axesData[tag] = {
					"particles": particles,
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

		# bring up Font Info → Exports so the user can see the new particles:
		try:
			thisFont.parent.windowController().showFontInfoWindowWithTabSelected_(2)
		except Exception as e:
			print(f"\n\t⚠️ Could not open Font Info → Exports: {e}")

		Glyphs.showNotification("Insert Instances", "Done. Details in Macro Window.")


if Glyphs.versionNumber >= 4:
	InstanceMakerV4()
else:
	InstanceMaker()
