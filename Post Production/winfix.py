"""
winfix.py
Usage:
	python3 winfix.py [options] font1.ttf font2.ttf ...

Options:
	-h, --help      Show this help message and exit
	-u, --usage     Show usage information and exit
	-f, --force     Overwrite existing fvar tables if present
"""

import sys
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import _f_v_a_r

def addEmptyFvar(ttFont, filename, force=False):
	if 'fvar' in ttFont and not force:
		print(f'⚠️  fvar table already exists in {filename}. Use -f/--force to overwrite.')
		return False
	# Create a new empty fvar table
	fvar = _f_v_a_r.table__f_v_a_r()
	fvar.axes = []
	fvar.instances = []
	ttFont['fvar'] = fvar
	return True

def printUsage():
	usageText = """
winfix.py
Usage:
	python3 winfix.py [options] font1.ttf font2.ttf ...

Options:
	-h, --help      Show this help message and exit
	-u, --usage     Show usage information and exit
	-f, --force     Overwrite existing fvar tables if present
"""
	print(usageText)

def main():
	args = sys.argv[1:]
	force = False
	if not args or '-h' in args or '--help' in args or '-u' in args or '--usage' in args:
		printUsage()
		sys.exit(0)
	if '-f' in args:
		force = True
		args.remove('-f')
	if '--force' in args:
		force = True
		args.remove('--force')

	for fontPath in args:
		if fontPath.startswith('-'):
			continue
		try:
			font = TTFont(fontPath)
			success = addEmptyFvar(font, fontPath, force=force)
			if success:
				font.save(fontPath)
				print(f'✅ Added empty fvar in: {fontPath}')
		except Exception as e:
			print(f'‼️ Error processing {fontPath}: {e}')

if __name__ == '__main__':
	main()
