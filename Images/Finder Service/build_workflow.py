#!/usr/bin/env python3
"""
Builds “Trim Image to Content.workflow” (a Finder Quick Action) from trim_image.py.
The Python code is embedded in the workflow, so the .workflow is self-contained.
Run after every change of trim_image.py:  python3 build_workflow.py
"""

import os
import plistlib
import uuid

folder = os.path.dirname(os.path.abspath(__file__))
workflowName = "Trim Image to Content"
bundlePath = os.path.join(folder, f"{workflowName}.workflow", "Contents")

with open(os.path.join(folder, "trim_image.py"), encoding="utf-8") as scriptFile:
	pythonCode = scriptFile.read()

# Finder services get a minimal PATH, so look for a python3 that has Pillow:
shellScript = f"""for candidate in /opt/homebrew/bin/python3 /usr/local/bin/python3 /Library/Frameworks/Python.framework/Versions/Current/bin/python3 /usr/bin/python3; do
	if [ -x "$candidate" ] && "$candidate" -c "import PIL" 2>/dev/null; then
		"$candidate" - "$@" <<'TRIM_IMAGE_PYTHON'
{pythonCode}
TRIM_IMAGE_PYTHON
		exit $?
	fi
done
osascript -e 'display notification "Needs Python 3 with Pillow: pip3 install Pillow" with title "{workflowName}"'
"""

action = {
	"AMAccepts": {
		"Container": "List",
		"Optional": True,
		"Types": ["com.apple.cocoa.string"],
	},
	"AMActionVersion": "2.0.3",
	"AMApplication": ["Automator"],
	"AMParameterProperties": {
		"COMMAND_STRING": {},
		"CheckedForUserDefaultShell": {},
		"inputMethod": {},
		"shell": {},
		"source": {},
	},
	"AMProvides": {
		"Container": "List",
		"Types": ["com.apple.cocoa.string"],
	},
	"ActionBundlePath": "/System/Library/Automator/Run Shell Script.action",
	"ActionName": "Run Shell Script",
	"ActionParameters": {
		"COMMAND_STRING": shellScript,
		"CheckedForUserDefaultShell": True,
		"inputMethod": 1,  # pass input as arguments
		"shell": "/bin/bash",
		"source": "",
	},
	"BundleIdentifier": "com.apple.RunShellScript",
	"CFBundleVersion": "2.0.3",
	"CanShowSelectedItemsWhenRun": False,
	"CanShowWhenRun": True,
	"Category": ["AMCategoryUtilities"],
	"Class Name": "RunShellScriptAction",
	"InputUUID": str(uuid.uuid4()).upper(),
	"Keywords": ["Shell", "Script", "Command", "Run", "Unix"],
	"OutputUUID": str(uuid.uuid4()).upper(),
	"UUID": str(uuid.uuid4()).upper(),
	"UnlocalizedApplications": ["Automator"],
	"arguments": {},
	"isViewVisible": 1,
	"location": "309.000000:305.000000",
	"nibPath": "/System/Library/Automator/Run Shell Script.action/Contents/Resources/Base.lproj/main.nib",
}

document = {
	"AMApplicationBuild": "523",
	"AMApplicationVersion": "2.10",
	"AMDocumentVersion": "2",
	"actions": [{"action": action}],
	"connectors": {},
	"workflowMetaData": {
		"applicationBundleIDsByPath": {},
		"applicationPaths": [],
		"inputTypeIdentifier": "com.apple.Automator.fileSystemObject.image",
		"outputTypeIdentifier": "com.apple.Automator.nothing",
		"presentationMode": 15,
		"processesInput": 0,
		"serviceApplicationBundleID": "com.apple.finder",
		"serviceApplicationPath": "/System/Library/CoreServices/Finder.app",
		"serviceInputTypeIdentifier": "com.apple.Automator.fileSystemObject.image",
		"serviceOutputTypeIdentifier": "com.apple.Automator.nothing",
		"serviceProcessesInput": 0,
		"systemImageName": "NSActionTemplate",
		"useAutomaticInputType": 0,
		"workflowTypeIdentifier": "com.apple.Automator.servicesMenu",
	},
}

info = {
	"NSServices": [{
		"NSBackgroundColorName": "background",
		"NSIconName": "NSActionTemplate",
		"NSMenuItem": {"default": workflowName},
		"NSMessage": "runWorkflowAsService",
		"NSRequiredContext": {"NSApplicationIdentifier": "com.apple.finder"},
		"NSSendFileTypes": ["public.image"],
	}],
}

os.makedirs(bundlePath, exist_ok=True)
with open(os.path.join(bundlePath, "document.wflow"), "wb") as outputFile:
	plistlib.dump(document, outputFile)
with open(os.path.join(bundlePath, "Info.plist"), "wb") as outputFile:
	plistlib.dump(info, outputFile)
print(f"Built {workflowName}.workflow")
