#MenuTitle: OTVar Player
# -*- coding: utf-8 -*-
__doc__="""
Plays a glyph in Preview.
"""

import vanilla, threading, time, os

def saveFileInLocation( content="blabla", fileName="test.txt", filePath="~/Desktop" ):
	saveFileLocation = "%s/%s" % (filePath,fileName)
	saveFileLocation = saveFileLocation.replace( "//", "/" )
	f = open( saveFileLocation, 'w' )
	print "Exporting to:", f.name
	f.write( content )
	f.close()
	return True

class OTVarGlyphAnimator( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 350
		windowHeight = 90
		windowWidthResize  = 700 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"OTVar Player", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.OTVarGlyphAnimator.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		self.w.slider = vanilla.Slider( (15,12,-15,15), tickMarkCount=None, callback=self.redrawPreview, continuous=True, sizeStyle="regular", minValue=0, maxValue=100 )
		self.w.slower = vanilla.Button((15, -20-15, 47, -15), u"🚶", sizeStyle='regular', callback=self.slower )
		self.w.slower.getNSButton().setToolTip_("Slower")
		self.w.faster = vanilla.Button((65, -20-15, 47, -15), u"🏃", sizeStyle='regular', callback=self.faster )
		self.w.faster.getNSButton().setToolTip_("Faster")
		self.w.backAndForth = vanilla.CheckBox( (125, -20-15, 50, -15), u"⇋", value=False, callback=self.SavePreferences, sizeStyle='small' )
		
		
		# web button:
		self.w.buildWeb = vanilla.Button((-140,-35, -100,-15), u"🌍", sizeStyle='regular', callback=self.buildWeb )
		
		# Run Button:
		self.w.runButton = vanilla.Button((-95, -35, -15, -15), "Play", sizeStyle='regular', callback=self.togglePlay )
		self.w.runButton.getNSButton().setToolTip_("Toggle Play/Pause")
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print "Note: 'OTVar Glyph Animator' could not load preferences. Will resort to defaults"
		
		self.direction = 1
		self.font = Glyphs.font
		self.originalWeightValue = None
		self.isPlaying = False
		if self.font.instances:
			self.originalWeightValue = self.font.instances[0].weightValue
		self.w.bind("close",self.restoreFont)
		
		# open and initialize the preview area at the bottom
		self.redrawPreview(None)
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
	
	def windowIsClosing(self):
		try:
			self.isPlaying = False
			Glyphs.defaults["com.mekkablue.OTVarGlyphAnimator.slider"] = "0"
			return True
		except Exception as e:
			Glyphs.clearLog()
			Glyphs.showMacroWindow()
			print e
			print
			import traceback
			print traceback.format_exc()
			return False
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.OTVarGlyphAnimator.slider"] = self.w.slider.get()
			Glyphs.defaults["com.mekkablue.OTVarGlyphAnimator.backAndForth"] = self.w.backAndForth.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.OTVarGlyphAnimator.slider", 0)
			Glyphs.registerDefault("com.mekkablue.OTVarGlyphAnimator.delay", 0.05)
			Glyphs.registerDefault("com.mekkablue.OTVarGlyphAnimator.backAndForth", False)
			self.w.slider.set( Glyphs.defaults["com.mekkablue.OTVarGlyphAnimator.slider"] )
			self.w.backAndForth.set( Glyphs.defaults["com.mekkablue.OTVarGlyphAnimator.backAndForth"] )
		except:
			return False
			
		return True
	
	def setupWindow(self):
		if not self.font.tabs:
			tabText = "a"
			if self.font.selectedLayers:
				tabText = "".join([l.parent.name for l in self.font.selectedLayers])
			self.font.newTab(tabText)
		if self.font.currentTab.previewHeight <= 1.0:
			self.font.currentTab.previewHeight = 200
		if not self.font.instances:
			newInstance = GSInstance()
			newInstance.name = "Preview Instance"
			self.font.instances.append(newInstance)
		self.font.currentTab.previewInstances = self.font.instances[0]
	
	def restoreFont(self, sender):
		if not self.originalWeightValue is None:
			self.font.instances[0].weightValue = self.originalWeightValue
		else:
			self.font.instances = []
			
		# turn playing off when window is closed, otherwise it goes on forever:
		self.isPlaying = False
		
		# reset slider and redraw the preview area:
		Glyphs.defaults["com.mekkablue.OTVarGlyphAnimator.slider"] = 0
		Glyphs.redraw()
	
	def redrawPreview( self, sender ):
		try:
			self.setupWindow()
			
			# get Slider position
			sliderPos = self.w.slider.get() / 100.0
			weights = [m.weightValue for m in self.font.masters]
			if self.font.customParameters["Virtual Master"]:
				weights.append(self.font.customParameters["Virtual Master"][0]["Location"])
			minWt = min(weights)
			maxWt = max(weights)
			sliderWt = minWt + sliderPos * (maxWt-minWt)
			
			# apply to preview instance and redraw
			self.font.instances[0].weightValue = sliderWt
			self.font.currentTab.updatePreview()
			
			if not self.SavePreferences( self ):
				print "Note: 'OTVar Glyph Animator' could not write preferences."
		except Exception, e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print "OTVar Glyph Animator Error: %s" % e
			import traceback
			print traceback.format_exc()

	def togglePlay(self, sender):
		self.w.makeKey()
		self.isPlaying = not self.isPlaying
		if self.isPlaying:
			self.w.runButton.setTitle("Pause")
			self.play_(None)
		else:
			self.w.runButton.setTitle("Play")

	def play_( self, sender ):
		try:
			if not bool(Glyphs.defaults["com.mekkablue.OTVarGlyphAnimator.backAndForth"]):
				self.direction = 1
			
			# finer steps when played slowly:
			smoothnessFactor = 1
			if float(Glyphs.defaults["com.mekkablue.OTVarGlyphAnimator.delay"]) > 0.07:
				smoothnessFactor = 3
			elif float(Glyphs.defaults["com.mekkablue.OTVarGlyphAnimator.delay"]) > 0.05:
				smoothnessFactor = 2
			
			# execute an animation step:
			if self.isPlaying:
				# Move Slider:
				sliderPos = self.w.slider.get()
				if sliderPos >= 100:
					if not bool(Glyphs.defaults["com.mekkablue.OTVarGlyphAnimator.backAndForth"]):
						sliderPos = 0
					else:
						sliderPos = 99.9999
						self.direction = -1
				elif sliderPos <= 0:
					sliderPos = 0.0001
					if self.direction == -1:
						self.direction = 1
					
				else:
					sliderPos += self.direction * 2.0/smoothnessFactor
				self.w.slider.set( sliderPos )
				
				# Trigger Redraw:
				self.redrawPreview(None)
				self.font.currentTab.updatePreview()
				
				# Call this method again after a delay:
				playSignature = objc.selector(self.play_,signature='v@:')
				self.timer = NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
					float(Glyphs.defaults["com.mekkablue.OTVarGlyphAnimator.delay"])/smoothnessFactor, # interval
					self, # target
					playSignature, # selector
					None, # userInfo
					False # repeat
				)
		except Exception, e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print "OTVar Glyph Animator Error: %s" % e
			import traceback
			print traceback.format_exc()
			
	def slower(self, sender):
		delay = float(Glyphs.defaults["com.mekkablue.OTVarGlyphAnimator.delay"])
		if delay <= 0.1:
			delay += 0.01
			self.w.faster.enable(onOff=True)
		else:
			# disable slower button at slowest setting:
			self.w.slower.enable(onOff=False)
		Glyphs.defaults["com.mekkablue.OTVarGlyphAnimator.delay"] = delay
	
	def faster(self, sender):
		delay = float(Glyphs.defaults["com.mekkablue.OTVarGlyphAnimator.delay"])
		if delay > 0.02:
			delay -= 0.01
			self.w.slower.enable(onOff=True)
		else:
			# disable faster button at fastest setting:
			self.w.faster.enable(onOff=False)
		Glyphs.defaults["com.mekkablue.OTVarGlyphAnimator.delay"] = delay
	
	def buildWeb(self, sender):
		weightAxisPositions = []
		for m in self.font.masters:
			axisPos = m.customParameters["Axis Location"][0]["Location"]
			weightAxisPositions.append( int(axisPos) )
		if self.font.customParameters["Virtual Master"]:
			weightAxisPositions.append(self.font.customParameters["Virtual Master"][0]["Location"])
		
		firstAxisTag = "wght"
		if self.font.customParameters["Axes"]:
			firstAxisTag = self.font.customParameters["Axes"][0]["Tag"]
		
		htmlCode = """
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
@font-face {
	font-family: "%s";
	src: url("%sGX.ttf");
}
@keyframes Looper {
	from {
		font-variation-settings: "%s" %i;
	}
	to {
		font-variation-settings: "%s" %i;
	}
}
body {
	font: 360px "%s";
	animation: Looper %.1fs linear 0s infinite;
}
</style>
</head>
<body>%s</body>
</html>""" % (
			self.font.familyName,
			self.font.familyName,
			firstAxisTag,
			min(weightAxisPositions),
			firstAxisTag,
			max(weightAxisPositions),
			self.font.familyName,
			float(Glyphs.defaults["com.mekkablue.OTVarGlyphAnimator.delay"]) * 50,
			" ".join( ["&#x%s;" % g.unicode for g in self.font.glyphs if g.unicode and g.export ] )
		)
		
		exportPath = None
		if bool(Glyphs.defaults["GXPluginUseExportPath"]):
			exportPath = Glyphs.defaults["GXExportPath"]
		else:
			exportPath = Glyphs.defaults["GXExportPathManual"]
			
		print "exportPath:", exportPath
		if exportPath:
			if saveFileInLocation( content=htmlCode, fileName="font_animation.html", filePath=exportPath ):
				print "Successfully wrote file to disk."
				terminalCommand = 'cd "%s"; open .' % exportPath
				os.system( terminalCommand )
			else:
				print "Error writing file to disk."
		else:
			Message( 
				title="Cannot Create HTML for OTVar",
				message="Could not determine export path of your OTVar font. Export an OTVar font first, the HTML will be saved next to it.",
				OKButton=None
			)
		
OTVarGlyphAnimator()