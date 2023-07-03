#MenuTitle: Move Paths to Component
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Moves paths to a separate glyph and insert them as auto-aligned, anchored components in the source glyph. Perfect for making path+component mixtures into pure composites.
"""

import vanilla
from AppKit import NSNotificationCenter, NSPoint
from copy import copy as copy

class MovePathstoComponent(object):
	prefID = "com.mekkablue.MovePathstoComponent"
	prefDict = {
		# "prefName": defaultValue,
		"name": "_bar.dollar",
		"anchor": "bottom",
		"includeSpecialLayers": 0,
		"keepBaseComponentPosition": 1,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 350
		windowHeight = 180
		windowWidthResize = 100 # user can resize width by this value
		windowHeightResize = 0 # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight), # default window size
			"Move Paths to Component", # window title
			minSize=(windowWidth, windowHeight), # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize), # maximum size (for resizing)
			autosaveName=self.domain("mainwindow") # stores last window position and size
			)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.descriptionText = vanilla.TextBox(
			(inset, linePos + 2, -inset, 14), "Turn paths of selected glyph into component on all masters:", sizeStyle='small', selectable=True
			)
		linePos += lineHeight

		self.w.nameText = vanilla.TextBox((inset, linePos + 2, 100, 14), "Component name:", sizeStyle='small', selectable=True)
		self.w.name = vanilla.EditText((inset + 100, linePos, -inset - 30, 19), "_bar.dollar", callback=self.SavePreferences, sizeStyle='small')
		self.w.nameUpdateButton = vanilla.SquareButton((-inset - 20, linePos, -inset, 18), "↺", sizeStyle='small', callback=self.updateName)
		linePos += lineHeight

		self.w.anchorText = vanilla.TextBox((inset, linePos + 2, 100, 14), "Attach to anchor:", sizeStyle='small', selectable=True)
		self.w.anchor = vanilla.ComboBox((inset + 100, linePos - 1, -inset - 30, 19), self.allAnchorNames(), sizeStyle='small', callback=self.SavePreferences)
		self.w.anchorUpdateButton = vanilla.SquareButton((-inset - 20, linePos, -inset, 18), "↺", sizeStyle='small', callback=self.updateAnchors)
		linePos += lineHeight

		self.w.includeSpecialLayers = vanilla.CheckBox(
			(inset, linePos - 1, -inset, 20), "Include special layers (recommended)", value=True, callback=self.SavePreferences, sizeStyle='small'
			)
		linePos += lineHeight
		
		self.w.keepBaseComponentPosition = vanilla.CheckBox( (inset, linePos-1, -inset, 20), "Keep base component position (do not auto align 1st component)", value=False, callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		# Run Button:
		self.w.runButton = vanilla.Button((-140-inset, -20-inset, -inset, -inset), "Make Composite", sizeStyle='regular', callback=self.MovePathsToComponentMain)
		self.w.setDefaultButton(self.w.runButton)

		self.w.warningText = vanilla.TextBox((inset, -15-inset, -140-inset, 14), "", sizeStyle="small", selectable=True)

		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Move Paths to Component' could not load preferences. Will resort to defaults")

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def domain(self, prefName):
		prefName = prefName.strip().strip(".")
		return self.prefID + "." + prefName.strip()

	def pref(self, prefName):
		prefDomain = self.domain(prefName)
		return Glyphs.defaults[prefDomain]
	
	def updateUI(self, sender=None):
		# check for existing glyph:
		glyphName = self.w.name.get()
		glyphExistsInFont = Glyphs.font.glyphs[glyphName]
		self.w.runButton.enable(not glyphExistsInFont)
		if glyphExistsInFont:
			self.w.warningText.set(f"⚠️ {glyphName} already exists")
		else:
			self.w.warningText.set("")
		return True
		
	def SavePreferences( self, sender=None ):
		try:
			# write current settings into prefs:
			for prefName in self.prefDict.keys():
				Glyphs.defaults[self.domain(prefName)] = getattr(self.w, prefName).get()
			self.updateUI()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def LoadPreferences( self ):
		try:
			for prefName in self.prefDict.keys():
				# register defaults:
				Glyphs.registerDefault(self.domain(prefName), self.prefDict[prefName])
				# load previously written prefs:
				getattr(self.w, prefName).set( self.pref(prefName) )
			self.updateUI()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def updateAnchors(self, sender=None):
		anchorNames = self.allAnchorNames()
		self.w.anchor.setItems(anchorNames)
		
		glyphInfo = Glyphs.glyphInfoForName(self.w.name.get())
		if glyphInfo:
			possibleAnchors = glyphInfo.anchors
			if possibleAnchors:
				for anchorName in anchorNames:
					for possibleAnchorName in possibleAnchors:
						if anchorName in possibleAnchorName or possibleAnchorName in anchorName:
							self.w.anchor.set(anchorName)
							return
		
		for anchorName in anchorNames:
			if anchorName[0] == "#":
				self.w.anchor.set(anchorName)
				return

	def updateName(self, sender=None):
		thisFont = Glyphs.font
		if thisFont:
			if thisFont.selectedLayers:
				thisLayer = thisFont.selectedLayers[0]
				existingComponents = thisLayer.componentNames()
				thisGlyph = thisLayer.parent
				if thisGlyph:
					foundName = False
					if thisGlyph.glyphInfo and thisGlyph.glyphInfo.components:
						for compInfo in thisGlyph.glyphInfo.components[::-1]:
							compName = f"{compInfo.name}{'.case' if thisGlyph.case==GSUppercase and Glyphs.glyphInfoForName(compInfo.name).category=='Mark' else ''}".replace(".case.case", ".case")
							print(thisGlyph.name, compName)
							if not compName in existingComponents:
								self.w.name.set(compName)
								foundName = True
								break
					elif thisGlyph.name=="Q":
						self.w.name.set("_tail.Q")
						foundName = True
					if not foundName:
						self.w.name.set(f"_part.{thisGlyph.name}")
					self.SavePreferences()

	def allAnchorNames(self, sender=None):
		anchorNames = []
		thisFont = Glyphs.font
		if thisFont:
			if thisFont.selectedLayers:
				thisLayer = thisFont.selectedLayers[0]
				for thisAnchor in thisLayer.anchorsTraversingComponents():
					if not thisAnchor.name in anchorNames:
						anchorNames.append(thisAnchor.name)
		return anchorNames

	def MovePathsToComponentMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			if not self.SavePreferences():
				print("Note: 'Move Paths to Component' could not write preferences.")

			thisFont = Glyphs.font # frontmost font
			glyphName = None
			if thisFont is None:
				Message(title="No thisFont Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				print(f"‘Move Paths to Component’ Report for {thisFont.familyName}")
				if thisFont.filepath:
					print(thisFont.filepath)
				else:
					print("⚠️ The font file has not been saved yet.")
				print()

				# determine current glyph:
				if not thisFont.selectedLayers:
					Message(title="Error: No Glyph", message="The script requires a selected glyph. Best to open a glyph in Edit view.", OKButton="Oops")
					print("🚫 No glyph selected. Aborting.\nDone.")
					return

				thisGlyph = thisFont.selectedLayers[0].parent
				glyphName = thisGlyph.name
				if not thisGlyph.layers[0].paths:
					Message(
						title="Error: No Paths in Glyph",
						message="The glyph ‘%s’ seems to have no paths. So the script has nothing to turn into a component." % glyphName,
						OKButton="Oops"
						)
					print("🚫 No paths in first layer of %s. Aborting.\nDone." % glyphName)
					return

				print("⚒️ Processing %s..." % thisGlyph.name)

				# query prefs:
				newCompName = self.pref("name")
				category = self.pref("category")
				subCategory = self.pref("subCategory")
				attachToAnchor = str(self.pref("anchor"))
				includeSpecialLayers = self.pref("includeSpecialLayers")

				# determine the kind of comp glyph, and the name of the new anchor
				category = "Letter"
				subCategory = None
				if attachToAnchor.endswith("entry"):
					insertAnchor = attachToAnchor.replace("entry", "exit")
				elif attachToAnchor.endswith("exit"):
					insertAnchor = attachToAnchor.replace("exit", "entry")
				elif attachToAnchor.startswith("_"):
					insertAnchor = attachToAnchor[1:]
				else:
					insertAnchor = "_" + attachToAnchor
					category = "Mark"
					subCategory = "Nonspacing"

				# create new comp glyph:
				print("🔠 Creating %s..." % newCompName)
				newGlyph = GSGlyph()
				newGlyph.name = newCompName
				newGlyph.export = False
				newGlyph.category = category
				if subCategory:
					newGlyph.subCategory = subCategory
				if thisFont.glyphs[newCompName]:
					# overwrite if it already exists
					del thisFont.glyphs[newCompName]
					print("⚠️ Overwrote existing %s" % newCompName)
				thisFont.glyphs.append(newGlyph)

				# step through current glyph and extract paths to new comp glyph:
				for l in thisGlyph.layers:
					# extract paths:
					if l.isMasterLayer or (l.isSpecialLayer and includeSpecialLayers):
						originalWidth = l.width
						newLayer = copy(l)
						if l.components:
							originalFirstComponentPosition = l.components[0].position
						else:
							originalFirstComponentPosition = NSPoint(0,0)

						# get rid of components, we just want paths:
						if Glyphs.versionNumber >= 3:
							# GLYPHS 3
							for i in range(len(newLayer.shapes) - 1, -1, -1):
								thisShape = newLayer.shapes[i]
								if type(thisShape) == GSComponent:
									del newLayer.shapes[i]
						else:
							# GLYPHS 2
							for i in range(len(newLayer.components) - 1, -1, -1):
								del newLayer.components[i]

						# insert connecting anchor:
						newAnchor = GSAnchor()
						newAnchor.name = insertAnchor
						newAnchor.position = NSPoint(0, 0)
						for referralAnchor in l.anchorsTraversingComponents():
							if referralAnchor.name == attachToAnchor:
								newAnchor.position = referralAnchor.position
								break
						newLayer.anchors.append(newAnchor)

						# insert the new layer into the new comp glyph:
						if l.isMasterLayer:
							newGlyph.layers[l.associatedMasterId] = newLayer
						else:
							newGlyph.layers.append(newLayer)

						# in original glyph, insert component before or after:
						componentNames = None
						if "entry" in attachToAnchor or attachToAnchor.startswith("_"):
							componentNames = [newCompName]
							for c in l.components:
								componentNames.append(c.componentName)
						else:
							componentNames = []
							for c in l.components:
								componentNames.append(c.componentName)
							componentNames.append(newCompName)
						if componentNames:
							l.setComponentNames_(componentNames)

						# remove paths from original glyph, we just want to keep components:
						if Glyphs.versionNumber >= 3:
							# GLYPHS 3
							for i in range(len(l.shapes) - 1, -1, -1):
								thisShape = l.shapes[i]
								if type(thisShape) == GSPath:
									del l.shapes[i]
						else:
							# GLYPHS 2
							for i in range(len(l.paths) - 1, -1, -1):
								del l.paths[i]

						# autoalign all components and update metrics
						for i in range(len(l.components)):
							c = l.components[i]
							if self.pref("keepBaseComponentPosition") and i==0:
								c.alignment = -1
								c.position = originalFirstComponentPosition
							else:
								c.alignment = 1
						if not self.pref("keepBaseComponentPosition"):
							l.alignComponents() # updates the width

						# insert correcting RSB adjustment (minimum 5):
						widthDifference = originalWidth - l.width
						if abs(widthDifference) > 4:
							metricsKey = "==%s%i" % (
								"-" if widthDifference < 0 else "+",
								abs(widthDifference),
								)
							if attachToAnchor.endswith("exit"):
								l.leftMetricsKey = metricsKey
								leftOrRight = "left"
							elif attachToAnchor.endswith("entry"):
								l.rightMetricsKey = metricsKey
								leftOrRight = "right"
							else: # all other cases
								l.leftMetricsKey = metricsKey
								leftOrRight = "left"

							l.updateMetrics()
							l.syncMetrics()

							print("↔️ Added %s metrics key ‘%s’ on layer ‘%s’ (original width: %i)" % (
								leftOrRight,
								l.rightMetricsKey if leftOrRight=="right" else l.leftMetricsKey,
								l.name,
								originalWidth,
								))

			# trigger UI update:
			if Glyphs.versionNumber >= 3 and thisFont.currentTab:
				NSNotificationCenter.defaultCenter().postNotificationName_object_("GSUpdateInterface", thisFont.currentTab)

			# Final report:
			if glyphName:
				print("✅ Turned %s into a pure composite of %s." % (
					glyphName,
					" and ".join(componentNames),
					))
			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Move Paths to Component Error: %s" % e)
			import traceback
			print(traceback.format_exc())

MovePathstoComponent()
