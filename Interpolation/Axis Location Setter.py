# MenuTitle: Axis Location Setter
__doc__ = """
Batch-set axis locations for all instances with a certain name particle. E.g., set an axis location for all Condensed instances.
"""

import vanilla
from AppKit import NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityRequired, NSLayoutPriorityWindowSizeStayPut, NSTextAlignmentRight
from Foundation import NSDictionary
from GlyphsApp import Glyphs, GSFontMaster, Message
from mekkablue import mekkaObject, UpdateButton


def axisLocationEntry(axisName, locationValue):
	return NSDictionary.alloc().initWithObjects_forKeys_((axisName, locationValue), ("Axis", "Location"))


class AxisLocationSetter(mekkaObject):
	prefDict = {
		"particle": "Bold",
		"axisName": "Weight",
		"internalAxisValue": "",
		"externalAxisValue": "0",
		"includeInstances": False,
		"includeMasters": False,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 310
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Axis Location Setter",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15

		self.w.descriptionText1 = vanilla.TextBox("auto", "In all masters/instances with name particle", sizeStyle='small', selectable=True)

		self.w.particle = vanilla.ComboBox("auto", self.particlesOfCurrentFont(), sizeStyle='small', callback=self.SavePreferences)
		self.w.particleUpdateButton = UpdateButton("auto", callback=self.update)

		self.w.descriptionText2 = vanilla.TextBox("auto", "For axis", sizeStyle='small', selectable=True)
		self.w.axisName = vanilla.ComboBox("auto", self.axesOfCurrentFont(), sizeStyle='small', callback=self.SavePreferences)
		self.w.descriptionText21 = vanilla.TextBox("auto", ", set coordinates", sizeStyle='small', selectable=True)

		self.w.descriptionText3 = vanilla.TextBox("auto", "Internal", sizeStyle='small', selectable=True)
		self.w.internalAxisValue = vanilla.EditText("auto", "0", callback=self.SavePreferences, sizeStyle='small')
		self.w.internalAxisValue.getNSTextField().setPlaceholderString_("no change")
		self.w.descriptionText31 = vanilla.TextBox("auto", "→ External", sizeStyle='small', selectable=True)
		self.w.externalAxisValue = vanilla.EditText("auto", "0", callback=self.SavePreferences, sizeStyle='small')
		self.w.externalAxisValue.getNSTextField().setPlaceholderString_("no change")

		self.w.includeInstances = vanilla.CheckBox("auto", "Apply to instances", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.includeMasters = vanilla.CheckBox("auto", "Apply to masters", value=False, callback=self.SavePreferences, sizeStyle='small')

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Set", callback=self.AxisLocationSetterMain)
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; with everything hugging, the window
		# ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# labels in front of fields are right-aligned and share one width, so the fields line up;
		# the labels between two fields hug their text:
		labelNames = ("descriptionText2", "descriptionText3")
		for labelName in labelNames + ("descriptionText21", "descriptionText31"):
			nsLabel = getattr(self.w, labelName).getNSTextField()
			if labelName in labelNames:
				nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText1]-inset-|",
				"H:|-inset-[particle]-gap-[particleUpdateButton]-inset-|",
				"H:|-inset-[descriptionText2]-gap-[axisName(>=100)]-gap-[descriptionText21]-inset-|",
				"H:|-inset-[descriptionText3]-gap-[internalAxisValue(>=50)]-gap-[descriptionText31]-gap-[externalAxisValue(>=50)]-inset-|",
				"H:|-inset-[includeInstances]-gap-[includeMasters]-(>=inset)-|",
				"H:|-(>=inset)-[runButton(>=70)]-inset-|",
				"V:|-inset-[descriptionText1]-headlineGap-[particle]-row-[axisName]-row-[internalAxisValue]-row-[includeInstances]-inset-[runButton]-inset-|",
				# one baseline per row:
				{"view1": self.w.particleUpdateButton, "attribute1": "centerY", "view2": self.w.particle, "attribute2": "centerY"},
				{"view1": self.w.descriptionText2, "attribute1": "centerY", "view2": self.w.axisName, "attribute2": "centerY"},
				{"view1": self.w.descriptionText21, "attribute1": "centerY", "view2": self.w.axisName, "attribute2": "centerY"},
				{"view1": self.w.descriptionText3, "attribute1": "centerY", "view2": self.w.internalAxisValue, "attribute2": "centerY"},
				{"view1": self.w.descriptionText31, "attribute1": "centerY", "view2": self.w.internalAxisValue, "attribute2": "centerY"},
				{"view1": self.w.externalAxisValue, "attribute1": "centerY", "view2": self.w.internalAxisValue, "attribute2": "centerY"},
				{"view1": self.w.includeMasters, "attribute1": "centerY", "view2": self.w.includeInstances, "attribute2": "centerY"},
				# equal widths:
				{"view1": self.w.descriptionText2, "attribute1": "width", "view2": self.w.descriptionText3, "attribute2": "width"},
				{"view1": self.w.externalAxisValue, "attribute1": "width", "view2": self.w.internalAxisValue, "attribute2": "width"},
			],
			metrics={"inset": inset, "gap": 8, "row": 6, "headlineGap": 8},
		)

		# Load Settings:
		self.LoadPreferences()

		self.updateUI()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def update(self, sender=None):
		self.w.particle.setItems(self.particlesOfCurrentFont())
		self.w.axisName.setItems(self.axesOfCurrentFont())

	def updateUI(self, sender=None):
		onOff = self.w.includeInstances.get() or self.w.includeMasters.get()
		onOff = onOff and bool(self.w.particle.get().strip())
		self.w.runButton.enable(onOff)

	def particlesOfCurrentFont(self, sender=None):
		particles = []
		currentFont = Glyphs.font
		if currentFont:
			for i in (*currentFont.masters, *currentFont.instances):
				for particle in i.name.split(" "):
					if particle and particle not in particles:
						particles.append(particle)
				if i.name not in particles:
					particles.append(i.name)
			particles.sort()
		return particles

	def axesOfCurrentFont(self, sender=None):
		axes = []
		currentFont = Glyphs.font
		if currentFont:
			for a in currentFont.axes:
				if a.name not in axes:
					axes.append(a.name)
		return axes

	def setInternalCoordinate(self, thisInstance, thisAxisName, newAxisValue):
		theFont = thisInstance.font
		# axisLocations = []
		for i, thisAxis in enumerate(theFont.axes):
			if thisAxis.name == thisAxisName:
				thisInstance.setAxisValueValue_forId_(float(newAxisValue), thisAxis.axisId)
				return True
		return False

	def setAxisLocationCoordinate(self, thisInstance, thisAxisName, newAxisValue):
		paramName = "Axis Location"
		existingParameter = thisInstance.customParameters[paramName]

		theFont = thisInstance.font
		axisLocations = []
		for i, thisAxis in enumerate(theFont.axes):
			# determine the axis value:
			value = None
			if thisAxis.name == thisAxisName:
				# set the requested axis value:
				value = float(newAxisValue)
			elif existingParameter:
				# preserve existing axis value:
				for entry in existingParameter:
					if thisAxis.name == entry["Axis"]:
						value = entry["Location"]
			if value is None:
				# otherwise replicate internal coordinate:
				if isinstance(thisInstance, GSFontMaster):
					value = thisInstance.axisValueValueForId_(thisAxis.axisId)
				else:
					value = thisInstance.coordinateForAxisIndex_(i)

			# add axis location entry:
			axisLocations.append(axisLocationEntry(thisAxis.name, value))

		# add collected entries as axis location parameter:
		if axisLocations:
			thisInstance.customParameters[paramName] = tuple(axisLocations)
			return True

		return False

	def fontHasAxisWithName(self, font, axisName):
		for axis in font.axes:
			if axis.name == axisName:
				return True
		return False

	def particleIsPartOfName(self, particle, instanceName):
		# particle is the full name:
		if instanceName.strip() == particle.strip():
			return True

		# PROBLEM: finding particle "Bold Italic" (with whitespace) should not find "SemiBold Italic"
		delim = "🧙"
		modifiedInstanceName = delim.join(instanceName.split())
		modifiedParticle = delim.join(particle.split())

		# particle in the MIDDLE of the name:
		searchTerm = f"{delim}{modifiedParticle}{delim}"
		if searchTerm in modifiedInstanceName:
			return True

		# particle at the END of the name:
		searchTerm = f"{delim}{modifiedParticle}"
		if modifiedInstanceName.endswith(searchTerm):
			return True

		# particle at the BEGINNING of the name:
		searchTerm = f"{modifiedParticle}{delim}"
		if modifiedInstanceName.startswith(searchTerm):
			return True

		return False

	def AxisLocationSetterMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="Axis Location Setter requires a font. Open a font and run the script again.", OKButton=None)
			else:
				fileName = thisFont.filepath.lastPathComponent() if thisFont.filepath else f"{thisFont.familyName} (unsaved)"
				print(f"Axis Location Setter Report for {fileName}")
				print()

				particle = self.pref("particle")
				axisName = self.pref("axisName")
				internalAxisValue = self.pref("internalAxisValue")
				externalAxisValue = self.pref("externalAxisValue")
				includeInstances = self.pref("includeInstances")
				includeMasters = self.pref("includeMasters")

				if not self.fontHasAxisWithName(thisFont, axisName):
					Message(title="Axis Location Setter Error", message="The frontmost font does not have an axis called ‘%s’." % axisName, OKButton=None)
					print(f"❌ Axis ‘{axisName}’ not found.")
				else:
					thisFont.disableUpdateInterface()  # suppresses UI updates in Font View
					try:
						# set axis locations for instances:
						instanceCount = 0
						if includeInstances:
							for thisInstance in thisFont.instances:
								if self.particleIsPartOfName(particle, thisInstance.name):
									instanceCount += 1
									if externalAxisValue != "":
										if self.setAxisLocationCoordinate(thisInstance, axisName, externalAxisValue):
											print(f"ℹ️ EXTERNAL {axisName} = {externalAxisValue} in {thisInstance.name}")
									if internalAxisValue != "":
										if self.setInternalCoordinate(thisInstance, axisName, internalAxisValue):
											print(f"ℹ️ INTERNAL {axisName} = {internalAxisValue} in {thisInstance.name}")

						# set axis locations for masters:
						masterCount = 0
						if includeMasters:
							for thisMaster in thisFont.masters:
								if self.particleIsPartOfName(particle, thisMaster.name):
									masterCount += 1
									if externalAxisValue != "":
										if self.setAxisLocationCoordinate(thisMaster, axisName, externalAxisValue):
											print(f"Ⓜ️ EXTERNAL {axisName} = {externalAxisValue} in {thisMaster.name}")
									if internalAxisValue != "":
										if self.setInternalCoordinate(thisMaster, axisName, internalAxisValue):
											print(f"Ⓜ️ INTERNAL {axisName} = {internalAxisValue} in {thisMaster.name}")
					except Exception as e:
						raise e
					finally:
						thisFont.enableUpdateInterface()  # re-enables UI updates in Font View

					# Final report:
					message = f"Coordinates updated in {instanceCount} instances and {masterCount} masters. Details in Macro Window"
					print(f"\n{message}")
					Glyphs.showNotification(
						f"{thisFont.familyName}: Done",
						message,
					)

				print("\n✅ Done.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Axis Location Setter Error: %s" % e)
			import traceback
			print(traceback.format_exc())


if Glyphs.versionNumber >= 4:
	# GLYPHS 4
	Message(title="Axis Location Setter", message="This script is a helper for Glyphs 2 and 3. It is not meant for Glyphs 4 and does nothing there.", OKButton=None)
elif Glyphs.versionNumber >= 3:
	# GLYPHS 3
	AxisLocationSetter()
else:
	# GLYPHS 2
	Message(title="Axis Location Setter Error", message="This script requires at least Glyphs 3. Sorry.", OKButton=None)
