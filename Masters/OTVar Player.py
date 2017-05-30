#MenuTitle: OTVar Player
# -*- coding: utf-8 -*-
__doc__="""
Plays a glyph in Preview.
"""

import vanilla, threading, time
#from time import sleep, time

class OTVarGlyphAnimator( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 250
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
		
		# Run Button:
		self.w.runButton = vanilla.Button((-80-15, -20-15, -15, -15), "Play", sizeStyle='regular', callback=self.togglePlay )
		self.w.runButton.getNSButton().setToolTip_("Toggle Play/Pause")
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print "Note: 'OTVar Glyph Animator' could not load preferences. Will resort to defaults"

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
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			NSUserDefaults.standardUserDefaults().registerDefaults_(
				{
					"com.mekkablue.OTVarGlyphAnimator.slider": 0,
					"com.mekkablue.OTVarGlyphAnimator.delay": 0.05
				}
			)
			self.w.slider.set( Glyphs.defaults["com.mekkablue.OTVarGlyphAnimator.slider"] )
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
			# finer steps when played slowly:
			smoothnessFactor = 1
			if Glyphs.defaults["com.mekkablue.OTVarGlyphAnimator.delay"] > 0.07:
				smoothnessFactor = 3
			elif Glyphs.defaults["com.mekkablue.OTVarGlyphAnimator.delay"] > 0.05:
				smoothnessFactor = 2
			
			# execute an animation step:
			if self.isPlaying:
				# Move Slider:
				sliderPos = self.w.slider.get()
				if sliderPos >= 100:
					sliderPos = 0
				else:
					sliderPos += 2.0/smoothnessFactor
				self.w.slider.set( sliderPos )
				
				# Trigger Redraw:
				self.redrawPreview(None)
				self.font.currentTab.updatePreview()
				
				# Call this method again after a delay:
				playSignature = objc.selector(self.play_,signature='v@:')
				self.timer = NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
					Glyphs.defaults["com.mekkablue.OTVarGlyphAnimator.delay"]/smoothnessFactor, # interval
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
		if Glyphs.defaults["com.mekkablue.OTVarGlyphAnimator.delay"] <= 0.1:
			Glyphs.defaults["com.mekkablue.OTVarGlyphAnimator.delay"] += 0.01
			self.w.faster.enable(onOff=True)
		else:
			# disable slower button at slowest setting:
			self.w.slower.enable(onOff=False)
	
	def faster(self, sender):
		if Glyphs.defaults["com.mekkablue.OTVarGlyphAnimator.delay"] > 0.02:
			Glyphs.defaults["com.mekkablue.OTVarGlyphAnimator.delay"] -= 0.01
			self.w.slower.enable(onOff=True)
		else:
			# disable faster button at fastest setting:
			self.w.faster.enable(onOff=False)

OTVarGlyphAnimator()