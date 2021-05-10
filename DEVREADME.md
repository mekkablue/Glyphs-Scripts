# Developer Instructions

Want to add to the mekkablue scripts? Consider these style guides to keep the code consistent and legible for everyone.

Thanks!
— Rafał Buchner, Rainer Scheichelbauer

## Variable and contant names

* Keep your names legible: use `points`, not `p`.
* Do not repeat the type of the object in the variable name: `layers`, not `layerList` or `listOfLayers`. There are still remainders of ancient code where I was guilty of doing this myself, but we are cleaning this up, step by step ourselves.
* Please use `camelCase`. We know it is not very pythonic, but we have a lot of PyObjC pieces in our code, where underscores have a special meaning.

## Code conventions

* Use tabs, not spaces, for indentation.
* Be perfomance aware.
	* Use tuples wherever possible, instead of lists.
	* Consider `myTuple = (n for n in myList)` instead of `tuple(myList)`.
	* When in doubt, use the *timer* snippet (see below about snippets).

## Reporting

* Report into Macro Window.
* Use ‘Report for ...’ titles, consider clearing the Macro Window log at the beginning with `Glyphs.clearLog()`
* Use emojis (e.g. ⚠️✅❌☑️💾↔️🔠) and indentations to keep it legible and allow orientation for the user.

## Snippets

Are you using Sublime Text or TextMate? For frequent code pieces, consider the [Python for Glyphs snippets](https://github.com/mekkablue/Python-for-Glyphs "Python code snippets for the Glyphs.app font editor, for Sublime Text and TextMate") on GitHub.

