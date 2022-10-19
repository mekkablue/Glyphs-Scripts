# Developer Instructions

Want to contribute to the mekkablue scripts? Fantastic! Please, consider the suggestions in this style guide to keep the code consistent and legible for everyone.

Thanks!
— Rafał Buchner, Rainer Scheichelbauer

## Variable and constant names

* Keep your names legible: use `points`, not `p`.
* Do not repeat the type of the object in the variable name: `layers`, not `layerList` or `listOfLayers`. There are still remainders of ancient code where I was guilty of doing this myself, but we are cleaning this up, step by step ourselves.
* Please use `camelCase` , not `under_score_separations`. We know it is not very pythonic, but we have a lot of PyObjC pieces in our code, where underscores have a special meaning.

## Code conventions

* Use the `.style.yapf` that is provided on the root level of the repo: 
* Use tabs, not spaces, for indentation.
* Be perfomance aware.
	* Wherever possible, use tuples instead of lists.
	* Consider `myTuple = (n for n in myList)` instead of `tuple(myList)`.
	* When in doubt, use the *timer* snippet (see below about snippets).

## Reporting

* Report into Macro Window with `print()` functions.
* Use ‘Report for ...’ titles, and consider clearing the Macro Window log at the beginning with `Glyphs.clearLog()`
* Use emojis (e.g. ⚠️✅❌☑️💾↔️🔠) and indentations to keep it legible and allow orientation for the user.
* Do not open the Macro Window unless the report is the whole purpose of the script. Instead, consider a floating notification or dialog to tell the user that the script completed and that details are available in the Macro Window, e.g., like this: `Glyphs.showNotification("Font X: done", "Brief statistic of what happened. Details in Macro Window.")`. If you use a dialog, opening the Macro Window can be a button.


## Snippets

Are you using Sublime Text or TextMate? For frequent code pieces, consider the [Python for Glyphs snippets](https://github.com/mekkablue/Python-for-Glyphs "Python code snippets for the Glyphs.app font editor, for Sublime Text and TextMate") on GitHub.

