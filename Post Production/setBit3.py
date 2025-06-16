#!/usr/bin/env python3
import argparse
from fontTools.ttLib import TTFont

def modify_head_flags(font_path, output_path, bit3_value=1, bit13_value=1):
	with TTFont(font_path) as font:
		head = font['head']
		
		if bit3_value == 1:
			head.flags |= 1 << 3  # Set bit 3 (value 8)
		else:
			head.flags &= ~(1 << 3)  # Clear bit 3

		if bit13_value == 1:
			head.flags |= 1 << 13  # Set bit 13 (value 8192)
		else:
			head.flags &= ~(1 << 13)  # Clear bit 13
		
		font.save(output_path)

if __name__ == "__main__":
	parser = argparse.ArgumentParser(
		description='Modify head.flags bits 3 and 13 in OpenType fonts',
		)
	parser.add_argument(
		'fonts',
		nargs='+',
		help='input font files',
		)
	parser.add_argument(
		'-b',
		'--bit3',
		type=int,
		choices=[0,1],
		default=1,
		help='set bit 3 ‘integer scaling’ value (0 or 1, default=1)',
		)
	parser.add_argument(
		'-c',
		'--bit13',
		type=int,
		choices=[0,1],
		default=1,
		help='set bit 13 ‘ClearType’ value (0 or 1, default=1)',
		)
	parser.add_argument(
		'-o',
		'--output',
		help='output file (if not specified, will overwrite input file)',
		)
	
	args = parser.parse_args()
	
	for font_path in args.fonts:
		output = args.output or font_path
		modify_head_flags(font_path, output, args.bit3, args.bit13)
		if font_path != output:
			print(f"✅ Updated bit3={args.bit3}, bit13={args.bit13} in {font_path} -> {output}")
		else:
			print(f"✅ Updated bit3={args.bit3}, bit13={args.bit13} in {font_path}")
	print()