#MenuTitle: Rewire Fire
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Finds, selects and marks duplicate coordinates. Two nodes on the same position typically can be rewired with Reconnect Nodes.
"""

import vanilla
from Foundation import NSPoint

def isOnLine(p1,p2,p3, threshold=0.6):
	"""
	Returns True if p3 is on and within p1-p2.
	And not off more than threshold.
	"""
	x1,y1 = p1.x,p1.y
	x2,y2 = p2.x,p2.y
	x3,y3 = p3.x,p3.y

	dx = x2 - x1
	dy = y2 - y1
	d2 = dx*dx + dy*dy
	nx = ((x3-x1)*dx + (y3-y1)*dy) / d2

	if distance(p3, NSPoint(dx*nx + x1, dy*nx + y1)) < threshold:
		if 0.0 < nx < 1.0:
			return True

	return False

class RewireFire( object ):
	duplicateMarker = u"🔥"
	onSegmentMarker = u"🧨"
	
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 350
		windowHeight = 240
		windowWidthResize  = 100 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			u"%s Rewire Fire %s" % (self.duplicateMarker, self.onSegmentMarker) , # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.RewireFire.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.descriptionText = vanilla.TextBox( (inset, linePos+2, -inset, 14), u"Finds candidates for rewiring with Reconnect Nodes.", sizeStyle='small', selectable=True )
		linePos += lineHeight
		
		self.w.setFireToNode = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Mark duplicate nodes with fire emoji %s"%self.duplicateMarker, value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.setFireToNode.getNSButton().setToolTip_("Finds different on-curve nodes that share the same coordinates. Emoji will be added as a node name. Node names may disappear after reconnection and path cleanup.")
		linePos += lineHeight
		
		self.w.tolerateZeroSegments = vanilla.CheckBox( (inset*2, linePos-1, -inset*2, 20), u"Tolerate duplicate if it is neighboring node (OTVar)", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.tolerateZeroSegments.getNSButton().setToolTip_(u"If node coordinates within the same segment share the same coordinates, they will not be marked with a fire emoji. Makes sense in variable fonts, where segments need to disappear in a point in one master.")
		linePos += lineHeight
		
		
		# DISABLED
		# self.w.markWithCircle = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Circle duplicate coordinates with annotation ⭕️", value=False, callback=self.SavePreferences, sizeStyle='small' )
		# self.w.markWithCircle.getNSButton().setToolTip_("Circle annotations remain after reconnecting the nodes.")
		# linePos += lineHeight

		self.w.dynamiteForOnSegment = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Mark nodes on top of line segments with dynamite emoji %s"%self.onSegmentMarker, value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.dynamiteForOnSegment.getNSButton().setToolTip_("Finds on-curve nodes that are located on line segments between (other) two on-curve nodes. Emoji will be added as a node name. Node names may disappear after reconnection and path cleanup.")
		linePos += lineHeight

		self.w.shouldSelect = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Select nodes for rewiring on affected glyph layers", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.shouldSelect.getNSButton().setToolTip_("If nodes are found, will reset the layer selection and select only the affected nodes. In the best case, you should be able to right-click, hold down the Opt (Alt) key, and choose Reconnect Nodes on All Masters from the context menu.")
		linePos += lineHeight
		
		self.w.includeNonExporting = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Include non-exporting glyphs", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.includeNonExporting.getNSButton().setToolTip_("Also check in glyphs that are not set to export. Recommended if you have modular components in the font.")
		linePos += lineHeight
		
		self.w.openTabWithAffectedLayers = vanilla.CheckBox( (inset, linePos-1, 200, 20), u"New tab with affected layers", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.openTabWithAffectedLayers.getNSButton().setToolTip_("If checked, will open a new tab with all layers that contain duplicate coordinates. Otherwise, will report in Macro Window only.")
		self.w.reuseTab = vanilla.CheckBox( (inset+200, linePos-1, -inset, 20), u"Reuse current tab", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.reuseTab.getNSButton().setToolTip_("If enabled, will only open a new tab if there is none open yet. Otherwise will always open a new tab.")
		linePos += lineHeight
		
		self.w.progress = vanilla.ProgressBar((inset, linePos, -inset, 16))
		self.w.progress.set(0) # set progress indicator to zero
		linePos+=lineHeight
		
		self.w.statusText = vanilla.TextBox( (inset, -20-inset, -80-inset, -inset), u"🤖 Ready.", sizeStyle='small', selectable=True )
		linePos += lineHeight
		
		
		# Run Button:
		self.w.runButton = vanilla.Button( (-80-inset, -20-inset, -inset, -inset), "Fire", sizeStyle='regular', callback=self.RewireFireMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Rewire Fire' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
	
	def updateUI(self, sender=None):
		anyOptionSelected = self.w.setFireToNode.get() or self.w.dynamiteForOnSegment.get()
		self.w.runButton.enable(anyOptionSelected)
		self.w.reuseTab.enable(self.w.openTabWithAffectedLayers.get())
		self.w.tolerateZeroSegments.enable(self.w.setFireToNode.get())
	
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.RewireFire.openTabWithAffectedLayers"] = self.w.openTabWithAffectedLayers.get()
			Glyphs.defaults["com.mekkablue.RewireFire.reuseTab"] = self.w.reuseTab.get()
			Glyphs.defaults["com.mekkablue.RewireFire.setFireToNode"] = self.w.setFireToNode.get()
			Glyphs.defaults["com.mekkablue.RewireFire.tolerateZeroSegments"] = self.w.tolerateZeroSegments.get()
			Glyphs.defaults["com.mekkablue.RewireFire.includeNonExporting"] = self.w.includeNonExporting.get()
			Glyphs.defaults["com.mekkablue.RewireFire.dynamiteForOnSegment"] = self.w.dynamiteForOnSegment.get()
			Glyphs.defaults["com.mekkablue.RewireFire.shouldSelect"] = self.w.shouldSelect.get()
			
			self.updateUI()
			
			# DISABLED
			# Glyphs.defaults["com.mekkablue.RewireFire.markWithCircle"] = self.w.markWithCircle.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.RewireFire.openTabWithAffectedLayers", 0)
			Glyphs.registerDefault("com.mekkablue.RewireFire.reuseTab", 1)
			Glyphs.registerDefault("com.mekkablue.RewireFire.setFireToNode", 1)
			Glyphs.registerDefault("com.mekkablue.RewireFire.tolerateZeroSegments", 0)
			Glyphs.registerDefault("com.mekkablue.RewireFire.includeNonExporting", 1)
			Glyphs.registerDefault("com.mekkablue.RewireFire.dynamiteForOnSegment", 1)
			Glyphs.registerDefault("com.mekkablue.RewireFire.shouldSelect", 1)
			self.w.openTabWithAffectedLayers.set( Glyphs.defaults["com.mekkablue.RewireFire.openTabWithAffectedLayers"] )
			self.w.reuseTab.set( Glyphs.defaults["com.mekkablue.RewireFire.reuseTab"] )
			self.w.setFireToNode.set( Glyphs.defaults["com.mekkablue.RewireFire.setFireToNode"] )
			self.w.tolerateZeroSegments.set( Glyphs.defaults["com.mekkablue.RewireFire.tolerateZeroSegments"] )
			self.w.includeNonExporting.set( Glyphs.defaults["com.mekkablue.RewireFire.includeNonExporting"] )
			self.w.dynamiteForOnSegment.set( Glyphs.defaults["com.mekkablue.RewireFire.dynamiteForOnSegment"] )
			self.w.shouldSelect.set( Glyphs.defaults["com.mekkablue.RewireFire.shouldSelect"] )
			
			self.updateUI()

			# DISABLED
			# Glyphs.registerDefault("com.mekkablue.RewireFire.markWithCircle", 0)
			# self.w.markWithCircle.set( Glyphs.defaults["com.mekkablue.RewireFire.markWithCircle"] )
		except:
			return False
			
		return True
	
	def circleInLayerAtPosition( self, layer, position, width=25.0 ):
		circle = GSAnnotation()
		circle.type = CIRCLE
		circle.position = position
		circle.width = width
		layer.annotations.append(circle)
	
	def findNodesOnLines(self, l, dynamiteForOnSegment=True, shouldSelect=True):
		affectedNodes=[]
		
		# find line segments:
		for p in l.paths:
			if p.closed:
				for n1 in p.nodes:
					n2 = n1.nextNode
					if n2 and n1.type!=GSOFFCURVE and n2.type!=GSOFFCURVE:
						p1 = n1.position
						p2 = n2.position
						
						# make sure it is not a zero-lenth segment:
						if p1!=p2:
							
							# find other nodes that are exactly on the line segment:
							for pp in l.paths:
								if pp.closed:
									for n3 in pp.nodes:
										if n3!=n1 and n3!=n2 and n3.type!=GSOFFCURVE:
											p3 = n3.position
											
											# find projection with threshold:
											if isOnLine(p1,p2,p3, threshold=0.499):
												affectedNodes.append(n3)
		
		if affectedNodes:
			thisGlyph=l.parent
			print()
			print(u"%s, layer '%s': %i nodes on line segments" % (thisGlyph.name, l.name, len(affectedNodes)))
			for node in affectedNodes:
				print(u"   %s x %.1f, y %.1f" % (self.onSegmentMarker, node.x, node.y))
			
			for n3 in affectedNodes:
				if dynamiteForOnSegment:
					n3.name=self.onSegmentMarker
				if shouldSelect:
					l.selection.append(n3)
			return True
		else:
			return False
	
	def findDuplicates(self, thisLayer, setFireToNode=True, markWithCircle=False, shouldSelect=True, tolerateZeroSegments=False):
		allCoordinates = []
		duplicateCoordinates = []
		for thisPath in thisLayer.paths:
			for thisNode in thisPath.nodes:
				if thisNode.type != OFFCURVE:
					if thisNode.position in allCoordinates:
						if not tolerateZeroSegments or not thisNode.position in (thisNode.nextNode.position, thisNode.prevNode.position):
							# select node:
							if shouldSelect and not thisNode in thisLayer.selection:
								thisLayer.selection.append(thisNode)
							duplicateCoordinates.append(thisNode.position)
							if setFireToNode:
								thisNode.name = self.duplicateMarker
					else:
						allCoordinates.append(thisNode.position)
						if thisNode.name == self.duplicateMarker:
							thisNode.name = None
						
		if duplicateCoordinates:
			thisGlyph=thisLayer.parent
			print()
			print(u"%s, layer '%s': %i duplicates" % (thisGlyph.name, thisLayer.name, len(duplicateCoordinates)))
			for dupe in duplicateCoordinates:
				print(u"   %s x %.1f, y %.1f" % (self.duplicateMarker, dupe.x, dupe.y))
		
			# if markWithCircle:
			# 	coords = set([(p.x,p.y) for p in duplicateCoordinates])
			# 	for dupeCoord in coords:
			# 		x,y = dupeCoord
			# 		self.circleInLayerAtPosition( thisLayer, NSPoint(x,y) )
			
			return True
			
		else:
			return False

	def RewireFireMain( self, sender ):
		try:
			Glyphs.clearLog()
				
			# update settings to the latest user input:
			if not self.SavePreferences( self ):
				print("Note: 'Rewire Fire' could not write preferences.")
			
			includeNonExporting = Glyphs.defaults["com.mekkablue.RewireFire.includeNonExporting"]
			setFireToNode = Glyphs.defaults["com.mekkablue.RewireFire.setFireToNode"]
			shouldSelect = Glyphs.defaults["com.mekkablue.RewireFire.shouldSelect"]
			dynamiteForOnSegment = Glyphs.defaults["com.mekkablue.RewireFire.dynamiteForOnSegment"]
			tolerateZeroSegments = Glyphs.defaults["com.mekkablue.RewireFire.tolerateZeroSegments"]
			# markWithCircle = Glyphs.defaults["com.mekkablue.RewireFire.markWithCircle"]
			
			thisFont = Glyphs.font # frontmost font
			print("Rewire Fire Report for %s" % thisFont.familyName)
			if thisFont.filepath:
				print(thisFont.filepath)
			else:
				print("⚠️ Warning: file has not been saved yet.")
			
			affectedLayers = []
			numGlyphs = float(len(thisFont.glyphs))
			
			for i,thisGlyph in enumerate(thisFont.glyphs):
				self.w.progress.set(int(i/numGlyphs*100))
				self.w.statusText.set(u"🔠 Processing %s"%thisGlyph.name)
				
				if thisGlyph.export or includeNonExporting:
					for thisLayer in thisGlyph.layers:
						if thisLayer.isMasterLayer or thisLayer.isSpecialLayer:
							# reset selection if necessary:
							if shouldSelect:
								thisLayer.selection = None
							
							# mark and select duplicate nodes:
							if setFireToNode and self.findDuplicates(thisLayer, shouldSelect=shouldSelect, tolerateZeroSegments=tolerateZeroSegments):
								affectedLayers.append(thisLayer)
								
							# mark and select nodes on line segments:
							if dynamiteForOnSegment and self.findNodesOnLines(thisLayer, shouldSelect=shouldSelect):
								if not thisLayer in affectedLayers:
									affectedLayers.append(thisLayer)
			
			self.w.progress.set(0)
			self.w.statusText.set(u"✅ Done.")
			
			if not affectedLayers:
				Message(title="No Duplicates Found", message=u"Could not find any nodes for rewiring in %s."%thisFont.familyName, OKButton=u"😇 Cool")
			else:
				# Floating notification:
				Glyphs.showNotification( 
					u"%s: found nodes for rewiring" % (thisFont.familyName),
					u"Found nodes for rewiring on %i layers. Details in Macro Window."%len(affectedLayers),
					)
				
				# opens new Edit tab:
				if Glyphs.defaults["com.mekkablue.RewireFire.openTabWithAffectedLayers"]:
					if thisFont.currentTab and Glyphs.defaults["com.mekkablue.RewireFire.reuseTab"]:
						thisFont.currentTab.layers = affectedLayers
					else:
						newTab = thisFont.newTab()
						newTab.layers = affectedLayers
				
			self.w.close() # delete if you want window to stay open
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Rewire Fire Error: %s" % e)
			import traceback
			print(traceback.format_exc())

RewireFire()