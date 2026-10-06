# MenuTitle: UI Smoke Test
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals

__doc__ = """
Manually opens and closes every Vanilla window in the mekkablue scripts.

This is deliberately not part of UnitTest.py or CI. Run it inside Glyphs and
click Start when you want to smoke-test the script dialogs.
"""

import ast
import sys
import tokenize
import traceback
from datetime import datetime
from pathlib import Path

import vanilla
from AppKit import (
	NSApplication,
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultLow,
	NSLayoutPriorityWindowSizeStayPut,
	NSModalPanelRunLoopMode,
)
from Foundation import NSObject, NSRunLoop, NSRunLoopCommonModes, NSTimer
from GlyphsApp import Glyphs
from mekkablue import mekkaObject


repositoryRoot = Path(__file__).resolve().parent.parent
logPath = Path(__file__).resolve().with_name("UITest.log")
application = NSApplication.sharedApplication()
windowClassNames = {"FloatingWindow", "Window"}
excludedDirectoryNames = {".git", ".pytest_cache", "UnitTest", "__pycache__"}


def sourceCreatesVanillaWindow(source, path):
	"""Return whether source calls a window class imported from Vanilla."""
	tree = ast.parse(source, filename=str(path))
	vanillaNames = set()
	windowNames = set()

	for node in ast.walk(tree):
		if isinstance(node, ast.Import):
			for importedName in node.names:
				if importedName.name == "vanilla":
					vanillaNames.add(importedName.asname or importedName.name)
		elif isinstance(node, ast.ImportFrom) and node.module == "vanilla":
			for importedName in node.names:
				if importedName.name in windowClassNames:
					windowNames.add(importedName.asname or importedName.name)

	for node in ast.walk(tree):
		if not isinstance(node, ast.Call):
			continue
		calledObject = node.func
		if isinstance(calledObject, ast.Name) and calledObject.id in windowNames:
			return True
		if (
			isinstance(calledObject, ast.Attribute)
			and calledObject.attr in windowClassNames
			and isinstance(calledObject.value, ast.Name)
			and calledObject.value.id in vanillaNames
		):
			return True
	return False


def findUIScripts():
	"""Find executable repository scripts that construct a Vanilla window."""
	scriptPaths = []
	for path in sorted(repositoryRoot.rglob("*.py")):
		relativePath = path.relative_to(repositoryRoot)
		if any(part in excludedDirectoryNames for part in relativePath.parts):
			continue
		with tokenize.open(path) as sourceFile:
			source = sourceFile.read()
		firstLine = source.partition("\n")[0].lstrip()
		if not firstLine.startswith(("# MenuTitle:", "#MenuTitle:")):
			continue
		if sourceCreatesVanillaWindow(source, path):
			scriptPaths.append(path)
	return scriptPaths


def windowsCreatedSince(existingWindows):
	"""Return application windows that were not present before a script ran."""
	return [window for window in application.windows() if window not in existingWindows]


def resetLog():
	try:
		logPath.write_text("", encoding="utf-8")
	except Exception:
		print("Could not reset UI smoke-test log:\n%s" % traceback.format_exc())


def writeLog(message):
	line = "%s  %s" % (datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3], message)
	try:
		with logPath.open("a", encoding="utf-8") as logFile:
			logFile.write(line + "\n")
	except Exception:
		print("Could not write UI smoke-test log:\n%s" % traceback.format_exc())


class TimerTarget(NSObject):
	"""Objective-C timer target that safely owns a Python callback until it fires."""
	callback = None

	def timerFired_(self, timer):
		callback = self.callback
		self.callback = None
		if callback is not None:
			callback()


class UISmokeTest(mekkaObject):
	def __init__(self):
		self.scriptPaths = findUIScripts()
		self.results = []
		self.currentNamespace = None
		self.currentIndex = 0
		self.currentError = None
		self.currentNewWindows = []
		self.currentVisibleWindows = []
		self.currentCloseErrors = []
		self.deferredWindows = []
		self.retainedWindowObjects = []
		self.windowsBeforeScript = []
		self.closeTimer = None
		self.nextTimer = None
		self.timerTargets = []
		self.stopRequested = False
		self.skipClearLogEnabled = False
		self.executingScript = False
		self.closeAttempted = False
		self.currentResultRecorded = False

		windowWidth = 520
		windowHeight = 1
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"UI Smoke Test",
			autosaveName=self.domain("mainwindow"),
		)
		self.w.descriptionText = vanilla.TextBox(
			"auto",
			"Opens each mekkablue GUI script in turn, then closes its window. "
			"No action buttons in the tested dialogs are pressed.",
			sizeStyle="small",
		)
		self.w.delayLabel = vanilla.TextBox("auto", "Seconds per dialog:", sizeStyle="small")
		self.w.delay = vanilla.EditText("auto", "0.25", sizeStyle="small")
		self.w.progress = vanilla.ProgressBar("auto", maxValue=max(1, len(self.scriptPaths)))
		self.w.status = vanilla.TextBox(
			"auto",
			"Ready: %i GUI scripts found." % len(self.scriptPaths),
			sizeStyle="small",
		)
		self.w.logPathText = vanilla.TextBox("auto", "Log: %s" % logPath, sizeStyle="small", selectable=True)
		self.w.stopButton = vanilla.Button("auto", "Stop", callback=self.stop)
		self.w.startButton = vanilla.Button("auto", "Start", callback=self.start)
		self.w.stopButton.enable(False)
		self.w.setDefaultButton(self.w.startButton)

		self.w.descriptionText.getNSTextField().setContentCompressionResistancePriority_forOrientation_(
			NSLayoutPriorityDefaultLow,
			NSLayoutConstraintOrientationHorizontal,
		)
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(
				NSLayoutPriorityWindowSizeStayPut,
				NSLayoutConstraintOrientationVertical,
			)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[delayLabel]-gap-[delay(55)]-(>=inset)-|",
				"H:|-inset-[progress]-inset-|",
				"H:|-inset-[status]-inset-|",
				"H:|-inset-[logPathText]-inset-|",
				"H:|-(>=inset)-[stopButton(>=70)]-gap-[startButton(>=70)]-inset-|",
				(
					"V:|-gap-[descriptionText(34)]-row-[delay]-row-[progress(16)]-row-[status]"
					"-row-[logPathText]-inset-[startButton]-inset-|"
				),
				"V:[stopButton]-inset-|",
				{
					"view1": self.w.delayLabel,
					"attribute1": "centerY",
					"view2": self.w.delay,
					"attribute2": "centerY",
				},
			],
			metrics={"inset": 15, "gap": 8, "row": 8},
		)
		self.w.open()
		self.w.makeKey()

	def schedule(self, delay, callback):
		target = TimerTarget.alloc().init()
		target.callback = callback
		self.timerTargets.append(target)
		timer = NSTimer.scheduledTimerWithTimeInterval_target_selector_userInfo_repeats_(
			delay,
			target,
			"timerFired:",
			None,
			False,
		)
		mainRunLoop = NSRunLoop.mainRunLoop()
		mainRunLoop.addTimer_forMode_(timer, NSRunLoopCommonModes)
		mainRunLoop.addTimer_forMode_(timer, NSModalPanelRunLoopMode)
		return timer

	def setSkipClearLog(self, value):
		try:
			Glyphs.setSkipClearLog_(value)
		except Exception:
			writeLog("COULD NOT SET skipClearLog=%s:\n%s" % (value, traceback.format_exc().rstrip()))
			return False
		self.skipClearLogEnabled = value
		writeLog("SET skipClearLog=%s" % value)
		return True

	def start(self, sender=None):
		try:
			delay = float(self.w.delay.get())
		except (TypeError, ValueError):
			self.w.status.set("Enter a number of seconds between 0.05 and 5.0.")
			return
		if not 0.05 <= delay <= 5.0:
			self.w.status.set("Enter a number of seconds between 0.05 and 5.0.")
			return

		self.scriptPaths = findUIScripts()
		self.delay = delay
		self.results = []
		self.currentNamespace = None
		self.retainedWindowObjects = []
		self.currentIndex = 0
		self.stopRequested = False
		resetLog()
		writeLog("RUN START: %i GUI scripts; %.2f seconds per dialog" % (len(self.scriptPaths), self.delay))
		if not self.setSkipClearLog(True):
			self.w.status.set("Could not prevent scripts from clearing the Macro window. See the log.")
			return
		self.w.progress.set(0)
		self.w.delay.enable(False)
		self.w.startButton.enable(False)
		self.w.stopButton.enable(True)
		try:
			self.nextTimer = self.schedule(0.05, self.runNextScript)
		except Exception:
			writeLog("COULD NOT START RUN:\n%s" % traceback.format_exc().rstrip())
			self.setSkipClearLog(False)
			self.w.delay.enable(True)
			self.w.startButton.enable(True)
			self.w.stopButton.enable(False)
			self.w.status.set("Could not start the UI test. See the log.")

	def stop(self, sender=None):
		self.stopRequested = True
		self.w.status.set("Stopping after the current dialog…")
		self.w.stopButton.enable(False)

	def runNextScript(self):
		if self.stopRequested or self.currentIndex >= len(self.scriptPaths):
			self.finish()
			return

		path = self.scriptPaths[self.currentIndex]
		relativePath = path.relative_to(repositoryRoot)
		print("UI Smoke Test %i/%i: %s" % (self.currentIndex + 1, len(self.scriptPaths), relativePath))
		writeLog("SCRIPT %i/%i START: %s" % (self.currentIndex + 1, len(self.scriptPaths), relativePath))
		self.w.status.set("%i/%i  %s" % (self.currentIndex + 1, len(self.scriptPaths), relativePath))
		self.currentError = None
		self.currentNewWindows = []
		self.currentVisibleWindows = []
		self.currentCloseErrors = []
		self.closeAttempted = False
		self.currentResultRecorded = False
		self.executingScript = True
		self.windowsBeforeScript = list(application.windows())
		self.closeTimer = self.schedule(self.delay, self.closeCurrentDialog)

		namespace = {
			"__file__": str(path),
			"__name__": "__main__",
			"__package__": None,
		}
		self.currentNamespace = namespace
		originalPath = list(sys.path)
		try:
			with tokenize.open(path) as sourceFile:
				source = sourceFile.read()
			sys.path.insert(0, str(path.parent))
			sys.path.insert(0, str(repositoryRoot.parent))
			exec(compile(source, str(path), "exec"), namespace)
		except BaseException:
			self.currentError = traceback.format_exc()
		finally:
			sys.path[:] = originalPath
			self.executingScript = False
		if self.currentError:
			writeLog("SCRIPT %i EXEC ERROR:\n%s" % (self.currentIndex + 1, self.currentError.rstrip()))
		else:
			writeLog("SCRIPT %i EXEC RETURNED" % (self.currentIndex + 1))
		if self.closeAttempted:
			self.closeDeferredWindows()
			self.recordCurrentResult()

	def closeCurrentDialog(self):
		self.currentNewWindows = windowsCreatedSince(self.windowsBeforeScript)
		self.currentVisibleWindows = [window for window in self.currentNewWindows if window.isVisible()]
		self.currentCloseErrors = []
		self.deferredWindows = []
		modalWindow = application.modalWindow()
		writeLog(
			"SCRIPT %i CLOSE START: %i new window(s), %i visible, modal=%s"
			% (
				self.currentIndex + 1,
				len(self.currentNewWindows),
				len(self.currentVisibleWindows),
				"yes" if modalWindow in self.currentNewWindows else "no",
			)
		)
		if modalWindow in self.currentNewWindows:
			try:
				writeLog("SCRIPT %i ABORTING MODAL WINDOW" % (self.currentIndex + 1))
				application.abortModal()
			except Exception:
				self.currentCloseErrors.append(traceback.format_exc())

		for window in reversed(self.currentNewWindows):
			try:
				try:
					windowTitle = window.title() or "<untitled>"
				except Exception:
					windowTitle = "<title unavailable>"
				writeLog("SCRIPT %i CLOSING WINDOW: %s" % (self.currentIndex + 1, windowTitle))
				self.retainedWindowObjects.append(window)
				windowDelegate = window.delegate()
				if windowDelegate is not None:
					self.retainedWindowObjects.append(windowDelegate)
				if window == modalWindow:
					window.orderOut_(None)
					self.deferredWindows.append(window)
					continue
				parentWindow = window.sheetParent()
				if parentWindow is not None:
					parentWindow.endSheet_(window)
				window.orderOut_(None)
				window.close()
			except Exception:
				self.currentCloseErrors.append(traceback.format_exc())
		writeLog("SCRIPT %i CLOSE CALLBACK RETURNING" % (self.currentIndex + 1))
		self.closeAttempted = True
		if not self.executingScript:
			self.closeDeferredWindows()
			self.recordCurrentResult()

	def closeDeferredWindows(self):
		for window in self.deferredWindows:
			try:
				writeLog("SCRIPT %i CLOSING DEFERRED MODAL WINDOW" % (self.currentIndex + 1))
				window.close()
			except Exception:
				self.currentCloseErrors.append(traceback.format_exc())
		self.deferredWindows = []

	def recordCurrentResult(self):
		if self.currentResultRecorded:
			return
		self.currentResultRecorded = True
		path = self.scriptPaths[self.currentIndex]
		if self.currentError:
			status = "ERROR"
			details = self.currentError
		elif self.currentCloseErrors:
			status = "CLOSE ERROR"
			details = "\n".join(self.currentCloseErrors)
		elif not self.currentVisibleWindows:
			status = "NO VISIBLE WINDOW"
			details = "The script did not show an application window."
		else:
			status = "OK"
			details = "%i visible window(s) opened and closed." % len(self.currentVisibleWindows)
		self.results.append((status, path, details))
		writeLog("SCRIPT %i RESULT: %s — %s" % (self.currentIndex + 1, status, path.relative_to(repositoryRoot)))
		self.currentNamespace = None

		self.currentIndex += 1
		self.w.progress.set(self.currentIndex)
		self.nextTimer = self.schedule(0.05, self.runNextScript)

	def finish(self):
		self.w.delay.enable(True)
		self.w.startButton.enable(True)
		self.w.stopButton.enable(False)
		problemResults = [result for result in self.results if result[0] != "OK"]
		wasStopped = self.stopRequested and self.currentIndex < len(self.scriptPaths)
		if wasStopped:
			self.w.status.set("Stopped after %i of %i scripts." % (self.currentIndex, len(self.scriptPaths)))
		else:
			self.w.status.set(
				"Finished: %i passed, %i need attention." % (len(self.results) - len(problemResults), len(problemResults))
			)

		if wasStopped:
			writeLog("RUN STOPPED: %i/%i scripts completed" % (self.currentIndex, len(self.scriptPaths)))
			print("UI Smoke Test stopped: %i/%i scripts completed." % (self.currentIndex, len(self.scriptPaths)))
		else:
			writeLog(
				"RUN FINISHED: %i passed; %i need attention"
				% (len(self.results) - len(problemResults), len(problemResults))
			)
			print(
				"UI Smoke Test finished: %i passed; %i need attention. Details: %s"
				% (len(self.results) - len(problemResults), len(problemResults), logPath)
			)
		if self.skipClearLogEnabled:
			self.setSkipClearLog(False)
		Glyphs.showMacroWindow()
		self.currentNamespace = None


UISmokeTest()
