#!/usr/bin/env python3
# subset.py - Font subsetter CLI using fontTools

import argparse
import glob
import os
import sys
from fontTools import subset
from fontTools.ttLib import TTFont

def main():
	parser = argparse.ArgumentParser(
		description='Subset fonts to specific charset and formats',
		formatter_class=argparse.RawDescriptionHelpFormatter,
		epilog="""
Examples:
  python3 subset.py -c "abcde" font.otf
  python3 subset.py -c "abcde" -f woff2,ttf -w *.ttf
  python3 subset.py -c "abcde fghij" -t -o myfont font.ttf
		"""
	)
	parser.add_argument('-c', '--charset', default=' ', help='Characters to include (default: space)')
	parser.add_argument('-f', '--formats', default='otf', help='Output formats: woff,woff2,otf,ttf,*')
	parser.add_argument('-w', '--webonly', action='store_true', help='Web-only: minimize name table')
	parser.add_argument('-t', '--test', action='store_true', help='Output minimal test.html')
	parser.add_argument('-o', '--output', help='Output base filename (default: original-subset)')
	parser.add_argument('fonts', nargs='+', help='TTF/OTF font files or glob patterns')
	args = parser.parse_args()

	formats = args.formats.split(',')
	if '*' in formats:
		formats = ['woff', 'woff2', 'otf', 'ttf']
	
	fontFiles = []
	for pattern in args.fonts:
		fontFiles.extend(glob.glob(pattern))
	
	if not fontFiles:
		print('No font files found.', file=sys.stderr)
		sys.exit(1)
	
	outputFonts = []
	for fontPath in fontFiles:
		if not os.path.isfile(fontPath):
			print(f'Skipping {fontPath}: not a file', file=sys.stderr)
			continue
		if not fontPath.lower().endswith(('.ttf', '.otf')):
			print(f'Skipping {fontPath}: not TTF/OTF', file=sys.stderr)
			continue
		
		if args.output:
			fontName = args.output
		else:
			name, ext = os.path.splitext(os.path.basename(fontPath))
			fontName = f'{name}-subset'
		
		options = subset.Options()
		options.text = ' ' + args.charset  # Always include space glyph first
		options.notdef_glyph = True
		
		if args.webonly:
			options.name_IDs = []  # Drop all name table entries for web-only
		
		try:
			font = TTFont(fontPath)
			subsetter = subset.Subsetter(options=options)
			subsetter.populate(text=' ' + args.charset)
			subsetter.subset(font)
			
			for fmt in formats:
				outPath = f'{fontName}.{fmt}'
				print(f'Writing {outPath}')
				saveOptions = subset.Options(flavor=fmt if fmt in ('woff', 'woff2') else None)
				font.save(outPath, saveOptions)
				outputFonts.append(outPath)
		except Exception as e:
			print(f'Error processing {fontPath}: {e}', file=sys.stderr)
	
	if args.test and outputFonts:
		htmlPath = 'test.html'
		fontFaces = '\n'.join([f'	@font-face {{ font-family: "{os.path.splitext(os.path.basename(f))[0]}"; src: url("{f}") format("{os.path.splitext(f)[1][1:].upper()}"); }}' for f in outputFonts])
		htmlContent = f'''<!DOCTYPE html>
<html>
<head>
{chr(10).join(fontFaces.splitlines())}
<style>
body {{ font-family: "{os.path.splitext(os.path.basename(outputFonts[0]))[0]}", sans-serif; font-size: 48px; }}
.test {{ white-space: pre-wrap; }}
</style>
</head>
<body>
<div class="test">
{args.charset}
</div>
</body>
</html>'''
		with open(htmlPath, 'w') as fh:
			fh.write(htmlContent)
		print(f'Wrote test file: {htmlPath}')

if __name__ == '__main__':
	main()
