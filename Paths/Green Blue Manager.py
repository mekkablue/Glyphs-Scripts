#MenuTitle: Green Blue Manager
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Define an angle above which a node will be set to blue, below which it will be set to green.
"""

import vanilla
from math import degrees, atan2
from Foundation import NSPoint, NSMutableArray, NSNumber

def angle( firstPoint, secondPoint ):
	"""
	Returns the angle (in degrees) of the straight line between firstPoint and secondPoint,
	0 degrees being the second point to the right of first point.
	firstPoint, secondPoint: must be NSPoint or GSNode
	"""
	xDiff = secondPoint.x - firstPoint.x
	yDiff = secondPoint.y - firstPoint.y
	return degrees(atan2(yDiff,xDiff))

class GreenBlueManager( object ):
	def __init__( self ):
		self.Tool = GlyphsPathPlugin.alloc().init()
		
		# Window 'self.w':
		windowWidth  = 300
		windowHeight = 265
		windowWidthResize  = 300 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Green Blue Manager", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.GreenBlueManager.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 5, 15, 22
		self.w.descriptionText = vanilla.TextBox( (inset, linePos+2, -inset, lineHeight*2), u"Validates the connection state of nodes, green vs. blue, according to the angle between them. Optionally corrects green/blue state and handles.", sizeStyle='small', selectable=True )
		linePos += lineHeight*2.5
		
		self.w.thresholdAngleText = vanilla.TextBox( (inset, linePos, 110, 14), u"Threshold Angle:", sizeStyle='small', selectable=True )
		self.w.thresholdAngle = vanilla.EditText( (inset+110, linePos-3, -inset, 19), "11", callback=self.SavePreferences, sizeStyle='small' )
		linePos += lineHeight
		
		self.w.completeFont = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Process complete font (otherwise selection)", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.completeFont.getNSButton().setToolTip_("If checked, will go through all active (i.e., master, brace and bracket) layers of all glyphs. If unchecked, will only go through selected layers. Careful: can take a minute.")
		linePos += lineHeight
		
		self.w.fixGreenBlue = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Fix green vs. blue connection for on-curves", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.fixGreenBlue.getNSButton().setToolTip_("Sets the green/blue state of an on-curve node according to the connection angle. Any connection below the threshold angle will be green, otherwise blue. Deselect both Fix and Realign options for a new tab with all glyphs that have nodes with wrong connections according to the threshold angle.")
		linePos += lineHeight
		
		self.w.realignHandles = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Realign handles attached to green nodes", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.realignHandles.getNSButton().setToolTip_("If a BCP (grey handle) follows a green node, it will be aligned to the previous two points. Deselect both Fix and Realign options for a new tab with all glyphs that have nodes with wrong connections according to the threshold angle.")
		linePos += lineHeight
		
		self.w.reportInMacroWindow = vanilla.CheckBox( (inset, linePos-1, 160, 20), u"Report in Macro window", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.reportInMacroWindowVerbose = vanilla.CheckBox( (inset+160, linePos-1, -inset, 20), u"Verbose", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.reportInMacroWindow.getNSButton().setToolTip_("If enabled, will output a report in Window > Macro Panel.")
		self.w.reportInMacroWindowVerbose.getNSButton().setToolTip_("If enabled, will output a verbose (detailed) report in Window > Macro Panel.")
		linePos += lineHeight
		
		self.w.shouldMark = vanilla.CheckBox( (inset, linePos-1, 160, 20), u"Mark affected nodes", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.shouldMark.getNSButton().setToolTip_(u"If enabled, will mark (intended) node type changes as follows: 💚=SMOOTH 🔷=CORNER.")
		self.w.reuseTab = vanilla.CheckBox( (inset+160, linePos-1, -inset, 20), u"Reuse current tab", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.reuseTab.getNSButton().setToolTip_(u"If enabled, will use the current tab for output, and only open a new tab if there is none open.")
		linePos += lineHeight
		
		self.w.progress = vanilla.ProgressBar((inset, linePos, -inset, 16))
		self.w.progress.set(0) # set progress indicator to zero
		linePos+=lineHeight
		
		self.w.processingText = vanilla.TextBox( (inset, linePos+2, -120-inset, 14), u"", sizeStyle='small', selectable=True )
		linePos += lineHeight
		
		
		# Run Button:
		self.w.runButton = vanilla.Button( (-120-inset, -20-inset, -inset, -inset), "Treat Points", sizeStyle='regular', callback=self.GreenBlueManagerMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Green Blue Manager' could not load preferences. Will resort to defaults")
		
		self.checkGUI()
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
	
	def checkGUI(self, sender=None):
		if not self.w.realignHandles.get() and not self.w.fixGreenBlue.get():
			self.w.runButton.setTitle("Open Tab")
		else:
			self.w.runButton.setTitle("Treat Nodes")
			
		self.w.reportInMacroWindowVerbose.enable( self.w.reportInMacroWindow.get() )
			
		
	def SavePreferences( self, sender=None ):
		self.checkGUI(sender=sender)
		try:
			Glyphs.defaults["com.mekkablue.GreenBlueManager.thresholdAngle"] = self.w.thresholdAngle.get()
			Glyphs.defaults["com.mekkablue.GreenBlueManager.completeFont"] = self.w.completeFont.get()
			Glyphs.defaults["com.mekkablue.GreenBlueManager.fixGreenBlue"] = self.w.fixGreenBlue.get()
			Glyphs.defaults["com.mekkablue.GreenBlueManager.realignHandles"] = self.w.realignHandles.get()
			Glyphs.defaults["com.mekkablue.GreenBlueManager.reportInMacroWindow"] = self.w.reportInMacroWindow.get()
			Glyphs.defaults["com.mekkablue.GreenBlueManager.reportInMacroWindowVerbose"] = self.w.reportInMacroWindowVerbose.get()
			Glyphs.defaults["com.mekkablue.GreenBlueManager.shouldMark"] = self.w.shouldMark.get()
			Glyphs.defaults["com.mekkablue.GreenBlueManager.reuseTab"] = self.w.reuseTab.get()
		except:
			return False
			
		return True

	def LoadPreferences( self, sender=None ):
		self.checkGUI(sender=sender)
		try:
			Glyphs.registerDefault( "com.mekkablue.GreenBlueManager.thresholdAngle", 11 )
			Glyphs.registerDefault( "com.mekkablue.GreenBlueManager.completeFont", 1 )
			Glyphs.registerDefault( "com.mekkablue.GreenBlueManager.fixGreenBlue", 1 )
			Glyphs.registerDefault( "com.mekkablue.GreenBlueManager.realignHandles", 1 )
			Glyphs.registerDefault( "com.mekkablue.GreenBlueManager.reportInMacroWindow", 1 )
			Glyphs.registerDefault( "com.mekkablue.GreenBlueManager.reportInMacroWindowVerbose", 0 )
			Glyphs.registerDefault( "com.mekkablue.GreenBlueManager.shouldMark", 0 )
			Glyphs.registerDefault( "com.mekkablue.GreenBlueManager.reuseTab", 1 )
			self.w.thresholdAngle.set( Glyphs.defaults["com.mekkablue.GreenBlueManager.thresholdAngle"] )
			self.w.completeFont.set( Glyphs.defaults["com.mekkablue.GreenBlueManager.completeFont"] )
			self.w.fixGreenBlue.set( Glyphs.defaults["com.mekkablue.GreenBlueManager.fixGreenBlue"] )
			self.w.realignHandles.set( Glyphs.defaults["com.mekkablue.GreenBlueManager.realignHandles"] )
			self.w.reportInMacroWindow.set( Glyphs.defaults["com.mekkablue.GreenBlueManager.reportInMacroWindow"] )
			self.w.reportInMacroWindowVerbose.set( Glyphs.defaults["com.mekkablue.GreenBlueManager.reportInMacroWindowVerbose"] )
			self.w.shouldMark.set( Glyphs.defaults["com.mekkablue.GreenBlueManager.shouldMark"] )
			self.w.reuseTab.set( Glyphs.defaults["com.mekkablue.GreenBlueManager.reuseTab"] )
		except:
			return False
			
		return True
	
	def realignLayer(self, thisLayer, shouldRealign=False, shouldReport=False, shouldVerbose=False):
		moveForward = NSPoint( 1, 0 )
		moveBackward = NSPoint( -1, 0 )
		noModifier = NSNumber.numberWithUnsignedInteger_(0)
		layerCount = 0
		
		if thisLayer:
			for thisPath in thisLayer.paths:
				oldPathCoordinates = [n.position for n in thisPath.nodes]
				for i,thisNode in enumerate(thisPath.nodes):
					if thisNode.type == GSOFFCURVE:
						# oldPosition = NSPoint(thisNode.position.x, thisNode.position.y)
						oncurve = None
						if thisNode.prevNode.type != GSOFFCURVE:
							oncurve = thisNode.prevNode
							opposingPoint = oncurve.prevNode
						elif thisNode.nextNode.type != GSOFFCURVE:
							oncurve = thisNode.nextNode
							opposingPoint = oncurve.nextNode
						
						handleStraight = (oncurve.x-thisNode.x) * (oncurve.y-thisNode.y) == 0.0
						if oncurve and oncurve.smooth and not handleStraight:
							# thisNode = angled handle, straighten it
							thisPath.setSmooth_withCenterPoint_oppositePoint_(
								thisNode,
								oncurve.position,
								opposingPoint.position,
							)
						elif oncurve and oncurve.smooth and handleStraight and opposingPoint.type == GSOFFCURVE:
							# thisNode = straight handle: align opposite handle
							thisPath.setSmooth_withCenterPoint_oppositePoint_(
								opposingPoint,
								oncurve.position,
								thisNode.position,
							)
						else:
							selectedNode = NSMutableArray.arrayWithObject_(thisNode)
							thisLayer.setSelection_( selectedNode )
							self.Tool.moveSelectionLayer_shadowLayer_withPoint_withModifier_( thisLayer, thisLayer, moveForward, noModifier )
							self.Tool.moveSelectionLayer_shadowLayer_withPoint_withModifier_( thisLayer, thisLayer, moveBackward, noModifier )
				
				for i,coordinate in enumerate(oldPathCoordinates):
					if thisPath.nodes[i].position != coordinate:
						layerCount += 1
				
						# put handle back if not desired by user:
						if not shouldRealign:
							thisPath.nodes[i].position = coordinate
		thisLayer.setSelection_( () )
		
		if shouldReport and shouldVerbose:
			if layerCount:
				if shouldRealign:
					print(u"   ⚠️ Realigned %i handle%s." % ( layerCount, "" if layerCount==1 else "s" ))
				else:
					print(u"   ❌ %i handle%s are unaligned." % ( layerCount, "" if layerCount==1 else "s" ))
			else:
				print(u"   ✅ All BCPs OK.")

		return layerCount
	
	def fixConnectionsOnLayer(self, thisLayer, shouldFix=False, shouldReport=False, shouldVerbose=False):
		thresholdAngle = float(Glyphs.defaults["com.mekkablue.GreenBlueManager.thresholdAngle"])
		shouldMark = bool(Glyphs.defaults["com.mekkablue.GreenBlueManager.shouldMark"])
		layerCount = 0
		for thisPath in thisLayer.paths:
			for i,thisNode in enumerate(thisPath.nodes):
				if thisNode.type == OFFCURVE:
					hotNode = None
					if thisNode.prevNode.type != OFFCURVE:
						hotNode = thisNode.prevNode
					elif thisNode.nextNode.type != OFFCURVE:
						hotNode = thisNode.nextNode
					if not hotNode is None:
						if hotNode.prevNode and hotNode.nextNode:
							angleDiff = abs( angle(hotNode.prevNode, hotNode) - angle(hotNode, hotNode.nextNode) ) % 360
							if (angleDiff <= thresholdAngle or angleDiff >= 360-thresholdAngle) and hotNode.connection != GSSMOOTH:
								layerCount += 1
								if shouldFix:
									hotNode.connection = GSSMOOTH
								if shouldMark:
									hotNode.name = u"💚"
							elif (thresholdAngle < angleDiff < 360-thresholdAngle) and hotNode.connection != GSSHARP:
								layerCount += 1
								if shouldFix:
									hotNode.connection = GSSHARP
								if shouldMark:
									hotNode.name = u"🔷"
		
		if shouldReport and shouldVerbose:
			print("%s, layer '%s'" % (thisLayer.parent.name, thisLayer.name))
			if layerCount:
				if shouldFix:
					print("   ⚠️ Fixed %s connection%s" % ( layerCount, "" if layerCount==1 else "s" ))
				else:
					print("   ❌ %s wrong connection%s" % ( layerCount, "" if layerCount==1 else "s" ))
			else:
				print("   ✅ All connections OK.")
		
		return layerCount
	
	def GreenBlueManagerMain( self, sender ):
		try:
			thisFont = Glyphs.font
			
			if not thisFont:
				Message(
					title="Green Blue Manager Error",
					message="Could not determine a frontmost font. The script requires at least one open font.",
					OKButton=None,
				)
			else:
				shouldRealign = Glyphs.defaults["com.mekkablue.GreenBlueManager.realignHandles"]
				shouldReport = Glyphs.defaults["com.mekkablue.GreenBlueManager.reportInMacroWindow"]
				shouldVerbose = Glyphs.defaults["com.mekkablue.GreenBlueManager.reportInMacroWindowVerbose"]
				shouldFix = Glyphs.defaults["com.mekkablue.GreenBlueManager.fixGreenBlue"]
				reuseTab = Glyphs.defaults["com.mekkablue.GreenBlueManager.reuseTab"]
				
				if shouldReport:
					Glyphs.clearLog()
			
				# determine which layers to process:
				if Glyphs.defaults["com.mekkablue.GreenBlueManager.completeFont"]:
					layersToBeProcessed = []
					for thisGlyph in thisFont.glyphs:
						for thisLayer in thisGlyph.layers:
							if thisLayer.isMasterLayer or thisLayer.isSpecialLayer:
								layersToBeProcessed.append(thisLayer)
				else:
					layersToBeProcessed = Glyphs.font.selectedLayers
			
				numberOfLayers = len(layersToBeProcessed)
				affectedLayersFixedConnections = []
				affectedLayersRealignedHandles = []
			
				# process layers:
				for i, thisLayer in enumerate(layersToBeProcessed):
					if type(thisLayer) != GSControlLayer:
						thisGlyph = thisLayer.parent
						statusMessage = "Processing: %s" % thisGlyph.name
						if shouldReport and shouldVerbose:
							print(statusMessage)
						self.w.processingText.set( statusMessage )
						self.w.progress.set(100.0/numberOfLayers*i)
						
						thisGlyph.beginUndo() # begin undo grouping
				
						numberOfFixes = self.fixConnectionsOnLayer( thisLayer, shouldFix=shouldFix )
						if numberOfFixes:
							affectedLayersFixedConnections.append( thisLayer )
				
						numberOfAligns = self.realignLayer( thisLayer, shouldRealign, shouldReport, shouldVerbose )
						if numberOfAligns:
							affectedLayersRealignedHandles.append( thisLayer )
				
						thisGlyph.endUndo()   # end undo grouping
				
				self.w.progress.set(100)
				statusMessage = "Processed %i layer%s." % (
					numberOfLayers,
					"" if numberOfLayers==1 else "s",
					)
				self.w.processingText.set( statusMessage )
				
				onlyReport = not shouldFix and not shouldRealign
				if onlyReport:
					titles = ("Wrong green-blue status","Unaligned BCPs")
				else:
					titles = ("Fixed green-blue status","Aligned BCPs")

				if shouldReport:
					if affectedLayersFixedConnections:
						print("\n%s in following layers:" % (titles[0]))
						for fixedLayer in affectedLayersFixedConnections:
							print("   %s, layer '%s'" % (fixedLayer.parent.name, fixedLayer.name))
					if affectedLayersRealignedHandles:
						print("\n%s in following layers:" % (titles[1]))
						for fixedLayer in affectedLayersRealignedHandles:
							print("   %s, layer '%s'" % (fixedLayer.parent.name, fixedLayer.name))
					
					print("\nDone. %s" % statusMessage)
					Glyphs.showMacroWindow()
			
				if numberOfLayers == 1 and Glyphs.font.currentTab:
					# if only one layer was processed, do not open new tab:
					Glyphs.font.currentTab.forceRedraw()
					if affectedLayersFixedConnections or affectedLayersRealignedHandles:
						message = u""
						if affectedLayersFixedConnections:
							message += u"• %s\n" % titles[0]
						if affectedLayersRealignedHandles:
							message += u"• %s\n" % titles[1]
						
						# Floating notification:
						Glyphs.showNotification( 
							"%s in %s:" % (
								"Found Problems" if onlyReport else "Fixed Problems",
								thisGlyph.name,
								), 
							message,
							)
					else:
						# Floating notification:
						Glyphs.showNotification( 
							"All OK in %s!" % thisGlyph.name,
							"No unaligned handles or wrong connection types found in glyph %s." % thisGlyph.name,
							)
						
				else:
					# opens new Edit tab:
					if affectedLayersFixedConnections or affectedLayersRealignedHandles:
						if not reuseTab or not thisFont.tabs:
							outputTab = thisFont.outputTab()
						else:
							outputTab = thisFont.currentTab
							outputTab.text = ""
							
						if affectedLayersFixedConnections:
							outputTab.text += "%s:\n" % titles[0]
							for affectedLayer in affectedLayersFixedConnections:
								outputTab.layers.append(affectedLayer)
						if affectedLayersFixedConnections and affectedLayersRealignedHandles:
							outputTab.text += "\n\n"
						if affectedLayersRealignedHandles:
							outputTab.text += "%s:\n" % titles[1]
							for affectedLayer in affectedLayersRealignedHandles:
								outputTab.layers.append(affectedLayer)
				
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("\nGreen Blue Manager Error: %s" % e)
			import traceback
			print(traceback.format_exc())
			print()

GreenBlueManager()