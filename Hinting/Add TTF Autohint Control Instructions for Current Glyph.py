#MenuTitle: Add TTF Autohint Control Instructions for Current Glyph
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
try:
	from builtins import str
except Exception as e:
	print("Warning: 'future' module not installed. Run 'sudo pip install future' in Terminal.")
__doc__="""
Adds a touch line for a given up/down amount to the Control Instructions of the current instance.
"""

from AppKit import NSPasteboard, NSStringPboardType
from Foundation import NSPoint
import math, vanilla

def sizeStringIsOK(sizeString):
	"""
	Checks if the size string adheres to the syntax.
	"""
	for character in sizeString:
		if not character in "1234567890-, ":
			return False
		elif character == "#":
			return True
	return True

def italic( yOffset, italicAngle=0.0, pivotalY=0.0 ):
	"""
	Returns the italicized position of an NSPoint 'thisPoint'
	for a given angle 'italicAngle' and the pivotal height 'pivotalY',
	around which the italic slanting is executed, usually half x-height.
	Usage: myPoint = italicize(myPoint,10,xHeight*0.5)
	"""
	x = 0.0
	#yOffset = thisPoint.y - pivotalY # calculate vertical offset
	italicAngle = math.radians( italicAngle ) # convert to radians
	tangens = math.tan( italicAngle ) # math.tan needs radians
	horizontalDeviance = tangens * yOffset # vertical distance from pivotal point
	return horizontalDeviance

def addToInstructions(instructionLine, currentInstance):
	parameterName = "TTFAutohint control instructions"
	currentInstanceName = currentInstance.name
	commentHeadline = "# %s" % currentInstanceName.upper()
	
	# determine existing instructions:
	instructions = currentInstance.customParameters[parameterName]
	
	# normalize single space after comma:
	instructionLine = instructionLine.replace(",",", ").replace("  "," ").replace("  "," ")
	
	# add to custom parameter:
	if instructions:
		if not instructions.startswith(commentHeadline):
			instructions = "%s\n%s" % (commentHeadline,instructions)
		currentInstance.customParameters[parameterName] = "%s\n%s" % (instructions,instructionLine)
	else:
		currentInstance.customParameters[parameterName] = "%s\n%s" % (commentHeadline,instructionLine)
		
	# trigger redraw for TTF Control Instructions Palette:
	thisFont = currentInstance.font
	if thisFont:
		NSNotificationCenter.defaultCenter().postNotificationName_object_("GSUpdateInterface", thisFont)

def setClipboard( myText ):
	"""
	Sets the contents of the clipboard to myText.
	Returns True if successful, False if unsuccessful.
	"""
	try:
		myClipboard = NSPasteboard.generalPasteboard()
		myClipboard.declareTypes_owner_( [NSStringPboardType], None )
		myClipboard.setString_forType_( myText, NSStringPboardType )
		return True
	except Exception as e:
		return False

def numberIndexStringFromNumbers(indexes):
	"""
	Turns sequence 1,2,3,4,7,8,9,10,14,19,21,22,23,27,30,31,32
	into "1-4, 7-10, 14, 19, 21-23, 27, 30-32"
	"""
	indexes = sorted( indexes )
	outputString = ""
	previousNumber = -100
	for i, thisNumber in enumerate(indexes):
		if not outputString:
			outputString += str(thisNumber)
		else:
			if previousNumber == thisNumber-1:
				if outputString[-1] != "-":
					outputString += "-"
				elif i == len(indexes)-1:
					outputString += "%i" % thisNumber
			else:
				if outputString[-1] == "-":
					outputString += "%i" % previousNumber
				outputString += ", %i" % thisNumber
		previousNumber = thisNumber
	return outputString


class AddTTFAutohintControlInstructionsForCurrentGlyph( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 155
		windowHeight = 410
		windowWidthResize  = 400 # user can resize width by this value
		windowHeightResize = 100   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Add ttfAutohint Control Instructions for Current Glyph", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.AddTTFAutohintControlInstructionsForCurrentGlyph.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 24
		
		self.w.explanatoryText = vanilla.TextBox( (inset, linePos+2, -inset, 60), "Touch instruction with px offset for active glyph & instance, respects italic angle.", sizeStyle='small', selectable=True )
		linePos += 3*lineHeight
		
		sectionOptions = (
			"All Points",
			"Upper Half",
			"Upper Third",
			"Upper Quarter",
			"Lower Half",
			"Lower Third",
			"Lower Quarter",
		)
		self.w.sectionToMoveText = vanilla.TextBox( (inset, linePos+2, 38, 14), u"Touch", sizeStyle='small', selectable=True )
		self.w.sectionToMove = vanilla.PopUpButton( (inset+38, linePos, -inset, 17), sectionOptions, sizeStyle='small', callback=self.SavePreferences )
		linePos += lineHeight
		
		
		self.w.runButtonAdd100 = vanilla.Button( (inset, linePos, -inset, 20), "+1.00", sizeStyle='regular', callback=self.AddTTFAutohintControlInstructionsForCurrentGlyphMain )
		linePos += lineHeight
		self.w.runButtonAdd075 = vanilla.Button( (inset, linePos, -inset, 20), "+0.75", sizeStyle='regular', callback=self.AddTTFAutohintControlInstructionsForCurrentGlyphMain )
		linePos += lineHeight
		self.w.runButtonAdd050 = vanilla.Button( (inset, linePos, -inset, 20), "+0.50", sizeStyle='regular', callback=self.AddTTFAutohintControlInstructionsForCurrentGlyphMain )
		linePos += lineHeight
		self.w.runButtonAdd025 = vanilla.Button( (inset, linePos, -inset, 20), "+0.25", sizeStyle='regular', callback=self.AddTTFAutohintControlInstructionsForCurrentGlyphMain )
		linePos += lineHeight
		self.w.runButtonSub025 = vanilla.Button( (inset, linePos, -inset, 20), "-0.25", sizeStyle='regular', callback=self.AddTTFAutohintControlInstructionsForCurrentGlyphMain )
		linePos += lineHeight
		self.w.runButtonSub050 = vanilla.Button( (inset, linePos, -inset, 20), "-0.50", sizeStyle='regular', callback=self.AddTTFAutohintControlInstructionsForCurrentGlyphMain )
		linePos += lineHeight
		self.w.runButtonSub075 = vanilla.Button( (inset, linePos, -inset, 20), "-0.75", sizeStyle='regular', callback=self.AddTTFAutohintControlInstructionsForCurrentGlyphMain )
		linePos += lineHeight
		self.w.runButtonSub100 = vanilla.Button( (inset, linePos, -inset, 20), "-1.00", sizeStyle='regular', callback=self.AddTTFAutohintControlInstructionsForCurrentGlyphMain )
		linePos += lineHeight

		self.w.ppmText = vanilla.TextBox( (inset, linePos+2, 14, 14), "@", sizeStyle='small', selectable=True )
		self.w.ppm = vanilla.EditText( (inset+14, linePos, -inset, 19), "8-12,20", sizeStyle='small', callback=self.SavePreferences )
		linePos += lineHeight *1.5
		
		
		
		
		
		# self.w.upperHalf = vanilla.CheckBox( (inset, linePos-1, -inset, 20), "Upper half (one)", value=False, callback=self.SavePreferences, sizeStyle='small' )
		# linePos += lineHeight

		self.w.rightAtTop = vanilla.Button( (inset, linePos, -inset, 20), "right at top", sizeStyle='regular', callback=self.InsertRightAtTop )
		linePos += lineHeight
		
		self.w.leftAtTop = vanilla.Button( (inset, linePos, -inset, 20), "left at top", sizeStyle='regular', callback=self.InsertLeftAtTop )
		linePos += lineHeight
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Add ttfAutohint Control Instructions for Current Glyph' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.AddTTFAutohintControlInstructionsForCurrentGlyph.ppm"] = self.w.ppm.get()
			Glyphs.defaults["com.mekkablue.AddTTFAutohintControlInstructionsForCurrentGlyph.sectionToMove"] = self.w.sectionToMove.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.AddTTFAutohintControlInstructionsForCurrentGlyph.ppm", "8-12,20")
			Glyphs.registerDefault("com.mekkablue.AddTTFAutohintControlInstructionsForCurrentGlyph.sectionToMove", 0)
			self.w.ppm.set( Glyphs.defaults["com.mekkablue.AddTTFAutohintControlInstructionsForCurrentGlyph.ppm"] )
			self.w.sectionToMove.set( Glyphs.defaults["com.mekkablue.AddTTFAutohintControlInstructionsForCurrentGlyph.sectionToMove"] )
		except:
			return False
			
		return True
	
	def fontInstanceToolGlyphLayer(self):
		Font = Glyphs.font
	
		# determine current instance:
		currentInstance = Font.instances[ Font.currentTab.selectedInstance() ]
	
		# switch to Instructor tool:
		ttInstructorClass = NSClassFromString("GlyphsToolTrueTypeInstructor")
		Font.parent.windowController().setToolForClass_(ttInstructorClass)
		tool = Font.parent.windowController().toolForClass_(ttInstructorClass)
	
		# double check Instructor tool is on:
		if not tool.className() == "GlyphsToolTrueTypeInstructor":
			Message(title="Tool Error", message="TT Instructor tool (I) must be active", OKButton=None)
		else:
			# determine glyph name:
			layer = Font.currentTab.activeLayer()
			if not layer and tool.activeLayers():
				# fallback attempt if line above fails:
				layer = tool.activeLayers()[0]
			
			if not layer:
				Message(title="ttfAutohint Error", message="Cannot determine current glyph. Perhaps try closing and reopening the tab. Sorry.", OKButton=None)
			else:
				glyph = layer.glyph()
				glyphName = glyph.name

				# prefix comment with glyph name:
				addToInstructions( "# %s" % glyphName, currentInstance )
			
				# overwrite glyph name with production name, if any:
				if glyph.productionName:
					glyphName = glyph.productionName
			
				# tt outline:
				glyf = tool.valueForKey_("fontOutlineGlyf")
				glyfBounds = glyf.bounds()
			
				# tt points:
				coords = glyf.coordinates()
				pointCount = coords.count()
				
				return Font, currentInstance, tool, glyphName, layer, glyf, glyfBounds, coords, pointCount
				
		return None, None, None, None, None, None, None, None, None

	def InsertRightAtTop( self, sender ):
		Font, currentInstance, tool, glyphName, layer, glyf, glyfBounds, coords, pointCount = self.fontInstanceToolGlyphLayer()
		if not Font:
			print("ERROR: Could not determine font.")
		else:
			# add right instruction for topmost point if desired:
			highestPointIndex = -1
			highestY = -1000
			for i in range(pointCount):
				thisPoint = coords.pointAtIndex_(i)
				if thisPoint.y > highestY:
					highestPointIndex = i
					highestY = thisPoint.y
			if highestPointIndex > -1:
				instructionLine = "%s right %i" % (glyphName,highestPointIndex)
				addToInstructions(instructionLine, currentInstance)
			else:
				print("ERROR: Could not determine highest point in %s." % glyphName)
				
	def InsertLeftAtTop( self, sender ):
		Font, currentInstance, tool, glyphName, layer, glyf, glyfBounds, coords, pointCount = self.fontInstanceToolGlyphLayer()
		if not Font:
			print("ERROR: Could not determine font.")
		else:
			# add left instruction for topmost point if desired:
			highestPointIndex = -1
			highestY = -1000
			topBound = glyfBounds.origin.y + glyfBounds.size.height
			for i in range(pointCount):
				thisPoint = coords.pointAtIndex_(i)
				prevPoint = coords.pointAtIndex_((i-1)%pointCount)
				nextPoint = coords.pointAtIndex_((i+1)%pointCount)
				if thisPoint.y < topBound and thisPoint.y > highestY and thisPoint.y > prevPoint.y and thisPoint.y >= nextPoint.y and (thisPoint.x < prevPoint.x or nextPoint.x < thisPoint.x):
					highestPointIndex = i
					highestY = thisPoint.y
			if highestPointIndex > -1:
				instructionLine = "%s left %i" % (glyphName,highestPointIndex)
				addToInstructions(instructionLine, currentInstance)
			else:
				print("ERROR: Could not determine highest point in %s." % glyphName)
		
	def AddTTFAutohintControlInstructionsForCurrentGlyphMain( self, sender ):
		try:
			if not self.SavePreferences( self ):
				print("Note: 'Add ttfAutohint Control Instructions for Current Glyph' could not write preferences.")
			
			shift = float(sender.getTitle())
			print(shift)
			if shift:
				Font, currentInstance, tool, glyphName, layer, glyf, glyfBounds, coords, pointCount = self.fontInstanceToolGlyphLayer()
				if Font:
					# determine x/y move based on italic angle:
					currentMaster = Font.selectedFontMaster
					italicAngle = currentMaster.italicAngle
					if italicAngle:
						moveString = "x %1.2f y %1.2f" % ( italic(shift, italicAngle), shift )
					else:
						moveString = "y %1.2f" % shift
			
					# determine PPMs
					sizeString = Glyphs.defaults["com.mekkablue.AddTTFAutohintControlInstructionsForCurrentGlyph.ppm"]
					if not sizeString:
						print("ERROR: Could not determine PPMs, will use a default. Did you enter any?")
						sizeString = "17"
					elif not sizeStringIsOK(sizeString):
						print("ERROR: Illegal character found in PPM specification (%s), will use default instead." % sizeString)
						sizeString = "17"
				
					# build point indexes to be moved:
					sectionChoice = Glyphs.defaults["com.mekkablue.AddTTFAutohintControlInstructionsForCurrentGlyph.sectionToMove"]
					pointIndexString = None
					
					if sectionChoice > 0:
						pointIndexes = []

						# ranges:
						halfHeight = glyfBounds.origin.y + 0.5 * glyfBounds.size.height
						upperThird = glyfBounds.origin.y + 0.666667 * glyfBounds.size.height
						lowerThird = glyfBounds.origin.y + 0.333333 * glyfBounds.size.height
						upperQuarter = glyfBounds.origin.y + 0.75 * glyfBounds.size.height
						lowerQuarter = glyfBounds.origin.y + 0.25 * glyfBounds.size.height
						
						for i in range(pointCount):
							thisPoint = coords.pointAtIndex_(i)
							if sectionChoice == 1 and thisPoint.y > halfHeight:
								# Upper Half
								pointIndexes.append(i)
							elif sectionChoice == 2 and thisPoint.y > upperThird:
								# Upper Third
								pointIndexes.append(i)
							elif sectionChoice == 3 and thisPoint.y > upperQuarter:
								# Upper Quarter
								pointIndexes.append(i)
							elif sectionChoice == 4 and thisPoint.y < halfHeight:
								# Lower Half
								pointIndexes.append(i)
							elif sectionChoice == 5 and thisPoint.y < lowerThird:
								# Lower Third
								pointIndexes.append(i)
							elif sectionChoice == 6 and thisPoint.y < lowerQuarter:
								# Lower Quarter
								pointIndexes.append(i)
								
						if pointIndexes:
							pointIndexString = numberIndexStringFromNumbers(pointIndexes)
					else:
						# all points, choice = 0
						# count of tt paths:
						endPoints = glyf.endPtsOfContours()
						pathCount = len(glyf.endPtsOfContours())
						pointIndexStrings = []
						# all points, in ranges, separated by path:
						j = 0
						for i in range(pathCount):
							k = endPoints.elementAtIndex_(i)
							pointIndexStrings.append( "%i-%i"%(j,k) )
							j = k+1
						pointIndexString = ", ".join(pointIndexStrings)
				
					if not pointIndexString:
						print("ERROR: no point indexes matching your criteria could be found.")
					else:
						# build the instruction line:
						instructionLine = "%s touch %s %s @ %s" % ( 
							glyphName,
							pointIndexString,
							moveString,
							sizeString,
							)
			
						# add the instruction line to the parameter:
						if instructionLine:
							addToInstructions(instructionLine,currentInstance)

			
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Add ttfAutohint Control Instructions for Current Glyph Error: %s" % e)
			import traceback
			print(traceback.format_exc())

Glyphs.defaults["TTPreviewAlsoShowOffCurveIndexes"] = True
AddTTFAutohintControlInstructionsForCurrentGlyph()

