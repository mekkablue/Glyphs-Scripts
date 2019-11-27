#MenuTitle: Steal Metrics
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
try:
	from builtins import str
except Exception as e:
	print("Warning: 'future' module not installed. Run 'sudo pip install future' in Terminal.")

__doc__="""
Copy sidebearings, widths and/or metric keys (both on layer and glyph) from one font master to another.
"""

import vanilla, math
from AppKit import NSAffineTransform, NSAffineTransformStruct

class MetricsCopy( object ):
	"""GUI for copying glyph metrics from one font to another"""
	
	def __init__( self ):
		self.listOfMasters = []
		self.updateListOfMasters() 
		
		# Window 'self.w':
		windowWidth  = 400
		windowHeight = 220
		windowWidthResize  = 500 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Steal Metrics", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.MetricsCopy.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		
		self.w.descriptionText = vanilla.TextBox( (inset, linePos+2, -inset, 14), u"Open two fonts and select glyphs in the target font.", sizeStyle='small', selectable=True )
		linePos += lineHeight
		
		
		self.w.text_anchor = vanilla.TextBox( (inset, linePos+2, 130, 17), "Transfer metrics from:", sizeStyle='small')
		self.w.from_font = vanilla.PopUpButton( (inset+130, linePos, -inset, 17), self.listOfMasterNames(), sizeStyle='small', callback=self.buttonCheck)
		
		linePos += lineHeight
		self.w.text_value = vanilla.TextBox( (inset, linePos+2, 130, 17), "To selected glyphs in:", sizeStyle='small')
		self.w.to_font = vanilla.PopUpButton( (inset+130, linePos, -inset, 17), self.listOfMasterNames()[::-1], sizeStyle='small', callback=self.buttonCheck)
		
		linePos += lineHeight
		self.w.lsb   = vanilla.CheckBox( ( inset, linePos-1, 80, 20), "LSB", value=True, callback=self.buttonCheck, sizeStyle='small' )
		self.w.rsb   = vanilla.CheckBox( ( inset+80, linePos-1, 80, 20), "RSB", value=True, callback=self.buttonCheck, sizeStyle='small' )
		self.w.width = vanilla.CheckBox( ( inset+80*2, linePos-1, 80, 20), "Width", value=False, callback=self.buttonCheck, sizeStyle='small' )
		self.w.lsb.getNSButton().setToolTip_("If enabled, will transfer values for left sidebearings.")
		self.w.rsb.getNSButton().setToolTip_("If enabled, will transfer values for right sidebearings.")
		self.w.width.getNSButton().setToolTip_("If enabled, will transfer values for advance widths.")
		
		
		linePos += lineHeight
		self.w.preferMetricKeys  = vanilla.CheckBox( (inset, linePos, -inset, 20), "Prefer (glyph and layer) metrics keys whenever available", value=False, sizeStyle='small', callback=self.buttonCheck )
		self.w.preferMetricKeys.getNSButton().setToolTip_("If enabled, will transfer the metrics key rather than the metric value, if a metrics key is persent in the source font.")
		
		linePos += lineHeight
		self.w.onlyMetricsKeys = vanilla.CheckBox( (inset*2, linePos-1, -inset, 20), u"Only transfer metrics keys (ignore LSB, RSB, Width)", value=False, callback=self.buttonCheck, sizeStyle='small' )
		self.w.onlyMetricsKeys.enable(False)
		self.w.onlyMetricsKeys.getNSButton().setToolTip_("If enabled, will only transfer metrics keys and not change any metric values. The checkboxes for LSB, RSB and Width will be disabled.")
		
		linePos += lineHeight
		self.w.ignoreSuffixes    = vanilla.CheckBox( (inset, linePos, 190, 20), "Ignore dotsuffix in source glyph:", value=False, sizeStyle='small', callback=self.buttonCheck )
		self.w.suffixToBeIgnored = vanilla.EditText( (inset+190, linePos, -inset, 20), ".alt", sizeStyle = 'small')
		self.w.suffixToBeIgnored.getNSTextField().setToolTip_(u"Will copy metrics from source glyph ‘eacute’ to target glyph ‘eacute.xxx’. Useful for transfering metrics to dotsuffixed glyph variants.")
		
		self.w.copybutton = vanilla.Button((-80-inset, -20-inset, -inset, -inset), "Transfer", sizeStyle='small', callback=self.copyMetrics)
		self.w.setDefaultButton( self.w.copybutton )
		
		if not self.LoadPreferences( ):
			self.outputError( "Could not load preferences at startup. Will resort to defaults." )
		
		self.w.open()
		self.w.makeKey()
		
		self.buttonCheck( None )
	
	def updateListOfMasters( self ):
		try:
			masterList = []
		
			for thisFont in Glyphs.fonts:
				for thisMaster in thisFont.masters:
					masterList.append( thisMaster )
			
			masterList.reverse() # so index accessing works as expected, and the default is: current font = target
			self.listOfMasters = masterList
		except:
			print(traceback.format_exc())
	
	def listOfMasterNames( self ):
		try:
			myMasterNameList = [ 
				"%i: %s - %s" % ( 
					i+1,
					self.listOfMasters[i].font.familyName,
					self.listOfMasters[i].name 
				) for i in range(len( self.listOfMasters ))
			]
			return myMasterNameList
		except:
			print(traceback.format_exc())
	
	def outputError( self, errMsg ):
		print("Steal Sidebearings Warning:", errMsg)
	
	def buttonCheck( self, sender ):
		try:
			# check if both font selection point to the same font
			# and disable action button if they do:
			fromFont = self.w.from_font.getItems()[ self.w.from_font.get() ]
			toFont   = self.w.to_font.getItems()[ self.w.to_font.get() ]
		
			if fromFont == toFont:
				self.w.copybutton.enable( onOff=False )
			else:
				self.w.copybutton.enable( onOff=True )
		
			# check if checkbox is enabled
			# and sync availability of text box
			suffixCheckBoxChecked = self.w.ignoreSuffixes.get()
			if suffixCheckBoxChecked:
				self.w.suffixToBeIgnored.enable( onOff=True )
			else:
				self.w.suffixToBeIgnored.enable( onOff=False )
			
			# All of LSB, RSB and Width must not be on at the same time:
			if self.w.rsb.get() and self.w.lsb.get() and self.w.width.get():
				if sender == self.w.rsb:
					self.w.width.set(False)
				else:
					self.w.rsb.set(False)
			
			# enable Only Keys option only if 
			if not self.w.preferMetricKeys.get():
				self.w.onlyMetricsKeys.set(False)
				
			self.w.onlyMetricsKeys.enable( bool(self.w.preferMetricKeys.get()) )
			metricValuesOnOff = not self.w.onlyMetricsKeys.get()
			self.w.lsb.enable(metricValuesOnOff)
			self.w.rsb.enable(metricValuesOnOff)
			self.w.width.enable(metricValuesOnOff)
		
			if not self.SavePreferences( self ):
				self.outputError( "Could not save preferences." )
		except:
			print(traceback.format_exc())
	
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.MetricsCopy.ignoreSuffixes"] = self.w.ignoreSuffixes.get()
			Glyphs.defaults["com.mekkablue.MetricsCopy.suffixToBeIgnored"] = self.w.suffixToBeIgnored.get()
			Glyphs.defaults["com.mekkablue.MetricsCopy.rsb"] = self.w.rsb.get()
			Glyphs.defaults["com.mekkablue.MetricsCopy.lsb"] = self.w.lsb.get()
			Glyphs.defaults["com.mekkablue.MetricsCopy.width"] = self.w.width.get()
			Glyphs.defaults["com.mekkablue.MetricsCopy.preferMetricKeys"] = self.w.preferMetricKeys.get()
			Glyphs.defaults["com.mekkablue.MetricsCopy.onlyMetricsKeys"] = self.w.onlyMetricsKeys.get()
			return True
		except:
			return False

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.MetricsCopy.ignoreSuffixes", 0)
			Glyphs.registerDefault("com.mekkablue.MetricsCopy.suffixToBeIgnored", ".alt")
			Glyphs.registerDefault("com.mekkablue.MetricsCopy.lsb", 0)
			Glyphs.registerDefault("com.mekkablue.MetricsCopy.rsb", 0)
			Glyphs.registerDefault("com.mekkablue.MetricsCopy.width", 0)
			Glyphs.registerDefault("com.mekkablue.MetricsCopy.preferMetricKeys", 0)
			Glyphs.registerDefault("com.mekkablue.MetricsCopy.onlyMetricsKeys", 0)
			self.w.ignoreSuffixes.set( Glyphs.defaults["com.mekkablue.MetricsCopy.ignoreSuffixes"] )
			self.w.suffixToBeIgnored.set( Glyphs.defaults["com.mekkablue.MetricsCopy.suffixToBeIgnored"] )
			self.w.lsb.set( Glyphs.defaults["com.mekkablue.MetricsCopy.lsb"] )
			self.w.rsb.set( Glyphs.defaults["com.mekkablue.MetricsCopy.rsb"] )
			self.w.width.set( Glyphs.defaults["com.mekkablue.MetricsCopy.width"] )
			self.w.preferMetricKeys.set( Glyphs.defaults["com.mekkablue.MetricsCopy.preferMetricKeys"] )
			self.w.onlyMetricsKeys.set( Glyphs.defaults["com.mekkablue.MetricsCopy.onlyMetricsKeys"] )
			return True
		except:
			return False
	
	def transform(self, shiftX=0.0, shiftY=0.0, rotate=0.0, skew=0.0, scale=1.0):
		"""
		Returns an NSAffineTransform object for transforming layers.
		Apply an NSAffineTransform t object like this:
			Layer.transform_checkForSelection_doComponents_(t,False,True)
		Access its transformation matrix like this:
			tMatrix = t.transformStruct() # returns the 6-float tuple
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
			myTransform.translateXBy_yBy_(shiftX,shiftY)
		if skew:
			skewStruct = NSAffineTransformStruct()
			skewStruct.m11 = 1.0
			skewStruct.m22 = 1.0
			skewStruct.m21 = math.tan(math.radians(skew))
			skewTransform = NSAffineTransform.transform()
			skewTransform.setTransformStruct_(skewStruct)
			myTransform.appendTransform_(skewTransform)
		return myTransform
	
	
	def copyMetrics(self, sender):
		if not self.SavePreferences( self ):
			self.outputError( "Could not save preferences." )
		
		preferMetricKeys = Glyphs.defaults["com.mekkablue.MetricsCopy.preferMetricKeys"]
		onlyMetricsKeys = Glyphs.defaults["com.mekkablue.MetricsCopy.onlyMetricsKeys"]
		fromFontIndex  = self.w.from_font.get()
		toFontIndex    = self.w.to_font.get() * -1 - 1
		sourceMaster   = self.listOfMasters[ fromFontIndex ]
		targetMaster   = self.listOfMasters[ toFontIndex ]
		sourceMasterID = sourceMaster.id
		targetMasterID = targetMaster.id
		sourceFont     = sourceMaster.font
		targetFont     = targetMaster.font
		ignoreSuffixes = Glyphs.defaults["com.mekkablue.MetricsCopy.ignoreSuffixes"]
		lsbIsSet = Glyphs.defaults["com.mekkablue.MetricsCopy.lsb"]
		rsbIsSet = Glyphs.defaults["com.mekkablue.MetricsCopy.rsb"]
		widthIsSet = Glyphs.defaults["com.mekkablue.MetricsCopy.width"]
		suffixToBeIgnored = self.w.suffixToBeIgnored.get().strip(".")
		selectedTargetLayers = targetFont.selectedLayers
		
		print("Transfering %i glyph metric%s from %s %s to %s %s:" % ( 
				len(selectedTargetLayers),
				"s" if abs(len(selectedTargetLayers))!=1 else "",
				sourceFont.familyName, sourceMaster.name,
				targetFont.familyName, targetMaster.name,
			))
		
		for targetLayer in [ targetFont.glyphs[l.parent.name].layers[targetMasterID] for l in selectedTargetLayers ]:
			try:
				targetGlyph = targetLayer.parent
				targetGlyphName = targetGlyph.name
				sourceGlyphName = targetGlyphName
				
				if ignoreSuffixes:
					# replace suffix in the middle of the name:
					sourceGlyphName = targetGlyphName.replace( ".%s." % suffixToBeIgnored, "." )
					# replace suffix at the end of the name:
					if sourceGlyphName.endswith( ".%s" % suffixToBeIgnored ):
						sourceGlyphName = sourceGlyphName[:-len(suffixToBeIgnored)-1]
					
				sourceGlyph = sourceFont.glyphs[ sourceGlyphName ]
				if not sourceGlyph:
					print("     %s: not found in source font" % sourceGlyphName)
				else:
					sourceLayer = sourceGlyph.layers[ sourceMasterID ]
					
					# go through metrics keys:
					metricsL, metricsR, metricsW = False, False, False
					if preferMetricKeys:
						if sourceGlyph.leftMetricsKey:
							targetGlyph.leftMetricsKey = sourceGlyph.leftMetricsKey
							metricsL = True
							print("     %s, left glyph key: '%s'" % ( targetGlyphName, targetGlyph.leftMetricsKey ))
						if sourceGlyph.rightMetricsKey:
							targetGlyph.rightMetricsKey = sourceGlyph.rightMetricsKey
							metricsR = True
							print("     %s, right glyph key: '%s'" % ( targetGlyphName, targetGlyph.rightMetricsKey ))
						if sourceGlyph.widthMetricsKey:
							targetGlyph.widthMetricsKey = sourceGlyph.widthMetricsKey
							metricsW = True
							print("     %s, width glyph key: '%s'" % ( targetGlyphName, targetGlyph.widthMetricsKey ))
						if sourceLayer.leftMetricsKey:
							targetLayer.leftMetricsKey = sourceLayer.leftMetricsKey
							metricsL = True
							print("     %s, left layer key: '%s'" % ( targetGlyphName, targetLayer.leftMetricsKey ))
						if sourceLayer.rightMetricsKey:
							targetLayer.rightMetricsKey = sourceLayer.rightMetricsKey
							metricsR = True
							print("     %s, right layer key: '%s'" % ( targetGlyphName, targetLayer.rightMetricsKey ))
						if sourceLayer.widthMetricsKey:
							targetLayer.widthMetricsKey = sourceLayer.widthMetricsKey
							metricsW = True
							print("     %s, width layer key: '%s'" % ( targetGlyphName, targetLayer.widthMetricsKey ))
					
					if not onlyMetricsKeys:
						# transfer numeric metrics:
						if lsbIsSet and not metricsL:
							targetLayer.LSB = sourceLayer.LSB
						if widthIsSet and not metricsW:
							targetLayer.width = sourceLayer.width
							if rsbIsSet and not metricsR: # set width AND rsb, i.e. adjust lsb:
								shift = targetLayer.RSB - sourceLayer.RSB
								shiftTransform = self.transform(shiftX=shift)
								targetLayer.transform_checkForSelection_doComponents_(shiftTransform,False,True)
						elif rsbIsSet and not metricsR:
							targetLayer.RSB = sourceLayer.RSB
					
						# update metrics:
						syncMessage = ""
						if metricsL or metricsR or metricsW:
							targetLayer.updateMetrics()
							targetLayer.syncMetrics()
							syncMessage =  ", synced metric keys"
					
						# report in macro window
						print("     %s: L %i, R %i, W %i%s" % ( 
							targetGlyphName, 
							targetLayer.LSB, targetLayer.RSB, targetLayer.width,
							syncMessage,
							))
				
			except Exception as e:
				self.outputError(e)
				import traceback
				print(traceback.format_exc())
		
MetricsCopy()
