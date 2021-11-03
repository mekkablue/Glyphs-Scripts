#MenuTitle: Set Label Colors
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Override the label colors for glyphs and layers.
"""

import vanilla
from Foundation import NSColor, NSArchiver, NSUnarchiver, NSKeyedArchiver

class SetLabelColors( object ):
	prefID = "com.mekkablue.SetLabelColors"
	
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 210
		windowHeight = 360
		windowWidthResize  = 10 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Set Label Colors", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = self.domain("mainwindow") # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		
		self.w.redText = vanilla.TextBox( (inset+20, linePos, 35, 19), "R", sizeStyle='small', selectable=False )
		self.w.greenText = vanilla.TextBox( (inset+60, linePos, 35, 19), "G", sizeStyle='small', selectable=False )
		self.w.blueText = vanilla.TextBox( (inset+100, linePos, 35, 19), "B", sizeStyle='small', selectable=False )
		self.w.alphaText = vanilla.TextBox( (inset+140, linePos, 35, 19), "A", sizeStyle='small', selectable=False )
		linePos += lineHeight
		
		self.w.color01 = vanilla.TextBox( (inset-1, linePos+2, 14, 14), "◼︎", sizeStyle='small' )
		self.w.red01 = vanilla.EditText( (inset+20, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.green01 = vanilla.EditText( (inset+60, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.blue01 = vanilla.EditText( (inset+100, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.alpha01 = vanilla.EditText( (inset+140, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		linePos += lineHeight

		self.w.color02 = vanilla.TextBox( (inset-1, linePos+2, 14, 14), "◼︎", sizeStyle='small' )
		self.w.red02 = vanilla.EditText( (inset+20, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.green02 = vanilla.EditText( (inset+60, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.blue02 = vanilla.EditText( (inset+100, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.alpha02 = vanilla.EditText( (inset+140, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		linePos += lineHeight

		self.w.color03 = vanilla.TextBox( (inset-1, linePos+2, 14, 14), "◼︎", sizeStyle='small' )
		self.w.red03 = vanilla.EditText( (inset+20, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.green03 = vanilla.EditText( (inset+60, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.blue03 = vanilla.EditText( (inset+100, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.alpha03 = vanilla.EditText( (inset+140, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		linePos += lineHeight

		self.w.color04 = vanilla.TextBox( (inset-1, linePos+2, 14, 14), "◼︎", sizeStyle='small' )
		self.w.red04 = vanilla.EditText( (inset+20, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.green04 = vanilla.EditText( (inset+60, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.blue04 = vanilla.EditText( (inset+100, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.alpha04 = vanilla.EditText( (inset+140, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		linePos += lineHeight

		self.w.color05 = vanilla.TextBox( (inset-1, linePos+2, 14, 14), "◼︎", sizeStyle='small' )
		self.w.red05 = vanilla.EditText( (inset+20, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.green05 = vanilla.EditText( (inset+60, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.blue05 = vanilla.EditText( (inset+100, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.alpha05 = vanilla.EditText( (inset+140, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		linePos += lineHeight

		self.w.color06 = vanilla.TextBox( (inset-1, linePos+2, 14, 14), "◼︎", sizeStyle='small' )
		self.w.red06 = vanilla.EditText( (inset+20, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.green06 = vanilla.EditText( (inset+60, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.blue06 = vanilla.EditText( (inset+100, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.alpha06 = vanilla.EditText( (inset+140, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		linePos += lineHeight

		self.w.color07 = vanilla.TextBox( (inset-1, linePos+2, 14, 14), "◼︎", sizeStyle='small' )
		self.w.red07 = vanilla.EditText( (inset+20, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.green07 = vanilla.EditText( (inset+60, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.blue07 = vanilla.EditText( (inset+100, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.alpha07 = vanilla.EditText( (inset+140, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		linePos += lineHeight

		self.w.color08 = vanilla.TextBox( (inset-1, linePos+2, 14, 14), "◼︎", sizeStyle='small' )
		self.w.red08 = vanilla.EditText( (inset+20, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.green08 = vanilla.EditText( (inset+60, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.blue08 = vanilla.EditText( (inset+100, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.alpha08 = vanilla.EditText( (inset+140, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		linePos += lineHeight

		self.w.color09 = vanilla.TextBox( (inset-1, linePos+2, 14, 14), "◼︎", sizeStyle='small' )
		self.w.red09 = vanilla.EditText( (inset+20, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.green09 = vanilla.EditText( (inset+60, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.blue09 = vanilla.EditText( (inset+100, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.alpha09 = vanilla.EditText( (inset+140, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		linePos += lineHeight

		self.w.color10 = vanilla.TextBox( (inset-1, linePos+2, 14, 14), "◼︎", sizeStyle='small' )
		self.w.red10 = vanilla.EditText( (inset+20, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.green10 = vanilla.EditText( (inset+60, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.blue10 = vanilla.EditText( (inset+100, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.alpha10 = vanilla.EditText( (inset+140, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		linePos += lineHeight

		self.w.color11 = vanilla.TextBox( (inset-1, linePos+2, 14, 14), "◼︎", sizeStyle='small' )
		self.w.red11 = vanilla.EditText( (inset+20, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.green11 = vanilla.EditText( (inset+60, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.blue11 = vanilla.EditText( (inset+100, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.alpha11 = vanilla.EditText( (inset+140, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		linePos += lineHeight

		self.w.color12 = vanilla.TextBox( (inset-1, linePos+2, 14, 14), "◼︎", sizeStyle='small' )
		self.w.red12 = vanilla.EditText( (inset+20, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.green12 = vanilla.EditText( (inset+60, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.blue12 = vanilla.EditText( (inset+100, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		self.w.alpha12 = vanilla.EditText( (inset+140, linePos, 35, 19), "0.5", sizeStyle='small', callback=self.SavePreferences)
		linePos += lineHeight

		
		# Run Button:
		# self.w.getButton = vanilla.Button( (-70-80*2-inset, -20-inset, -80*2-inset, -inset), "Current", sizeStyle='regular', callback=self.SetLabelColorsMain )
		self.w.resetButton = vanilla.Button( (-70-80-inset, -20-inset, -80-inset, -inset), "Reset", sizeStyle='regular', callback=self.SetLabelColorsMain )
		self.w.runButton = vanilla.Button( (-70-inset, -20-inset, -inset, -inset), "Set", sizeStyle='regular', callback=self.SetLabelColorsMain )
		self.w.setDefaultButton( self.w.runButton )
		
		self.setColors()
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Set Label Colors' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
	
	def resetColors(self):
		labelColors = NSMutableArray.alloc().initWithArray_([
			NSArchiver.archivedDataWithRootObject_(NSColor.colorWithDeviceRed_green_blue_alpha_(0.85, 0.26, 0.06, 0.5)),
			NSArchiver.archivedDataWithRootObject_(NSColor.colorWithDeviceRed_green_blue_alpha_(0.99, 0.62, 0.11, 0.5)),
			NSArchiver.archivedDataWithRootObject_(NSColor.colorWithDeviceRed_green_blue_alpha_(0.65, 0.48, 0.20, 0.5)),
			NSArchiver.archivedDataWithRootObject_(NSColor.colorWithDeviceRed_green_blue_alpha_(0.97, 0.90, 0.00, 0.5)),
			NSArchiver.archivedDataWithRootObject_(NSColor.colorWithDeviceRed_green_blue_alpha_(0.67, 0.95, 0.38, 0.5)),
			NSArchiver.archivedDataWithRootObject_(NSColor.colorWithDeviceRed_green_blue_alpha_(0.04, 0.57, 0.04, 0.5)),
			NSArchiver.archivedDataWithRootObject_(NSColor.colorWithDeviceRed_green_blue_alpha_(0.06, 0.60, 0.98, 0.5)),
			NSArchiver.archivedDataWithRootObject_(NSColor.colorWithDeviceRed_green_blue_alpha_(0.00, 0.20, 0.88, 0.5)),
			NSArchiver.archivedDataWithRootObject_(NSColor.colorWithDeviceRed_green_blue_alpha_(0.50, 0.09, 0.79, 0.5)),
			NSArchiver.archivedDataWithRootObject_(NSColor.colorWithDeviceRed_green_blue_alpha_(0.98, 0.36, 0.67, 0.5)),
			NSArchiver.archivedDataWithRootObject_(NSColor.colorWithDeviceRed_green_blue_alpha_(0.75, 0.75, 0.75, 0.5)),
			NSArchiver.archivedDataWithRootObject_(NSColor.colorWithDeviceRed_green_blue_alpha_(0.25, 0.25, 0.25, 0.5)),
			])
		Glyphs.defaults["LabelColors"] = labelColors
	
	def currentColors(self):
		# reset to defaults if nothing stored:
		if not Glyphs.defaults["LabelColors"]:
			self.resetColors()
		
		
		labelColorDatas = Glyphs.defaults["LabelColors"]
		newLabelColors = NSMutableArray.new()
		for colorData in labelColorDatas:
			color = NSUnarchiver.unarchiveObjectWithData_(colorData)
			newLabelColors.addObject_(color)
			labelColors = newLabelColors.copy()
		
	
	def setColors(self, sender=None):
		self.w.color01.getNSTextField().setTextColor_( NSColor.colorWithRed_green_blue_alpha_( float(self.w.red01.get()), float(self.w.green01.get()), float(self.w.blue01.get()), float(self.w.alpha01.get()), ))
		self.w.color02.getNSTextField().setTextColor_( NSColor.colorWithRed_green_blue_alpha_( float(self.w.red02.get()), float(self.w.green02.get()), float(self.w.blue02.get()), float(self.w.alpha02.get()), ))
		self.w.color03.getNSTextField().setTextColor_( NSColor.colorWithRed_green_blue_alpha_( float(self.w.red03.get()), float(self.w.green03.get()), float(self.w.blue03.get()), float(self.w.alpha03.get()), ))
		self.w.color04.getNSTextField().setTextColor_( NSColor.colorWithRed_green_blue_alpha_( float(self.w.red04.get()), float(self.w.green04.get()), float(self.w.blue04.get()), float(self.w.alpha04.get()), ))
		self.w.color05.getNSTextField().setTextColor_( NSColor.colorWithRed_green_blue_alpha_( float(self.w.red05.get()), float(self.w.green05.get()), float(self.w.blue05.get()), float(self.w.alpha05.get()), ))
		self.w.color06.getNSTextField().setTextColor_( NSColor.colorWithRed_green_blue_alpha_( float(self.w.red06.get()), float(self.w.green06.get()), float(self.w.blue06.get()), float(self.w.alpha06.get()), ))
		self.w.color07.getNSTextField().setTextColor_( NSColor.colorWithRed_green_blue_alpha_( float(self.w.red07.get()), float(self.w.green07.get()), float(self.w.blue07.get()), float(self.w.alpha07.get()), ))
		self.w.color08.getNSTextField().setTextColor_( NSColor.colorWithRed_green_blue_alpha_( float(self.w.red08.get()), float(self.w.green08.get()), float(self.w.blue08.get()), float(self.w.alpha08.get()), ))
		self.w.color09.getNSTextField().setTextColor_( NSColor.colorWithRed_green_blue_alpha_( float(self.w.red09.get()), float(self.w.green09.get()), float(self.w.blue09.get()), float(self.w.alpha09.get()), ))
		self.w.color10.getNSTextField().setTextColor_( NSColor.colorWithRed_green_blue_alpha_( float(self.w.red10.get()), float(self.w.green10.get()), float(self.w.blue10.get()), float(self.w.alpha10.get()), ))
		self.w.color11.getNSTextField().setTextColor_( NSColor.colorWithRed_green_blue_alpha_( float(self.w.red11.get()), float(self.w.green11.get()), float(self.w.blue11.get()), float(self.w.alpha11.get()), ))
		self.w.color12.getNSTextField().setTextColor_( NSColor.colorWithRed_green_blue_alpha_( float(self.w.red12.get()), float(self.w.green12.get()), float(self.w.blue12.get()), float(self.w.alpha12.get()), ))
		
	
	def domain(self, prefName):
		prefName = prefName.strip().strip(".")
		return self.prefID + "." + prefName.strip()
	
	def pref(self, prefName):
		prefDomain = self.domain(prefName)
		return Glyphs.defaults[prefDomain]
	
	def SavePreferences( self, sender=None ):
		try:
			# write current settings into prefs:
			Glyphs.defaults[self.domain("popup_1")] = self.w.popup_1.get()
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def LoadPreferences( self ):
		try:
			# register defaults:
			Glyphs.registerDefault(self.domain("popup_1"), 0)
			
			# load previously written prefs:
			self.w.popup_1.set( self.pref("popup_1") )
			return True
		except:
			import traceback
			print(traceback.format_exc())
			return False

	def SetLabelColorsMain( self, sender=None ):
		try:
			# clear macro window log:
			Glyphs.clearLog()
			
			# update settings to the latest user input:
			if not self.SavePreferences():
				print("Note: 'Set Label Colors' could not write preferences.")
			
			thisFont = Glyphs.font # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				print("Set Label Colors Report for %s" % thisFont.familyName)
				if thisFont.filepath:
					print(thisFont.filepath)
				else:
					print("⚠️ The font file has not been saved yet.")
				print()
			
				
				
			
	
			# Final report:
			Glyphs.showNotification( 
				"%s: Done" % (thisFont.familyName),
				"Set Label Colors is finished. Details in Macro Window",
				)
			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Set Label Colors Error: %s" % e)
			import traceback
			print(traceback.format_exc())

SetLabelColors()