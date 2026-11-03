#!/usr/bin/env python3
"""
Trims images to their content: the color of the top left pixel counts as
background, and the smallest rectangle that keeps every pixel of a different
color is cropped out. The result is saved next to the original as
“<name> trimmed.<ext>”; the original is never overwritten.

Usage: trim_image.py image1.png image2.jpg ...
Requires Pillow (pip3 install Pillow).
"""

import os
import subprocess
import sys

from PIL import Image, ImageChops, ImageOps


def contentBox(image):
	"""Returns (left, top, right, bottom) of everything that differs from the top left pixel, or None."""
	rgba = image.convert("RGBA")
	cornerColor = rgba.getpixel((0, 0))
	if cornerColor[3] == 0:
		# transparent background: all fully transparent pixels count as the same color
		return rgba.getchannel("A").getbbox()
	background = Image.new("RGBA", rgba.size, cornerColor)
	red, green, blue, alpha = ImageChops.difference(rgba, background).split()
	anyDifference = ImageChops.lighter(ImageChops.lighter(red, green), ImageChops.lighter(blue, alpha))
	return anyDifference.getbbox()


def freePath(path):
	base, extension = os.path.splitext(path)
	candidate = f"{base} trimmed{extension}"
	counter = 2
	while os.path.exists(candidate):
		candidate = f"{base} trimmed {counter}{extension}"
		counter += 1
	return candidate


def trimImage(path):
	"""Returns a (symbol, message) report line."""
	name = os.path.basename(path)
	with Image.open(path) as opened:
		imageFormat = opened.format
		if getattr(opened, "n_frames", 1) > 1:
			return "⚠️", f"{name}: skipped, multiple frames"
		info = dict(opened.info)
		image = ImageOps.exif_transpose(opened)  # so the top left is the top left you see
		image.load()
	box = contentBox(image)
	if box is None:
		return "⚠️", f"{name}: skipped, all pixels have the top left color"
	if box == (0, 0, image.width, image.height):
		return "☑️", f"{name}: nothing to trim"
	saveOptions = {}
	for key in ("icc_profile", "dpi", "exif"):
		if key in info:
			saveOptions[key] = info[key]
	if imageFormat == "JPEG":
		saveOptions["quality"] = 95
	outputPath = freePath(path)
	image.crop(box).save(outputPath, format=imageFormat, **saveOptions)
	return "✅", f"{name}: {image.width}×{image.height} → {box[2] - box[0]}×{box[3] - box[1]}, saved as {os.path.basename(outputPath)}"


def notify(message):
	script = f'display notification "{message}" with title "Trim Image to Content"'
	subprocess.run(["osascript", "-e", script], check=False)


def main(paths):
	reports = []
	for path in paths:
		try:
			reports.append(trimImage(path))
		except Exception as error:
			reports.append(("❌", f"{os.path.basename(path)}: {error}"))
	print("Trim Image to Content\n")
	for symbol, message in reports:
		print(f"\t{symbol} {message}")
	trimmedCount = sum(1 for symbol, _ in reports if symbol == "✅")
	problemCount = sum(1 for symbol, _ in reports if symbol in ("⚠️", "❌"))
	summary = f"{trimmedCount} of {len(reports)} trimmed"
	if problemCount:
		summary += f", {problemCount} with problems"
	if sys.platform == "darwin":
		notify(summary)


if __name__ == "__main__":
	main(sys.argv[1:])
