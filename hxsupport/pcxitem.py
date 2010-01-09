#!/usr/bin/python
import struct
import os
import Image, ImageDraw
import time
import unique

"""
*** PCX format ***
Bytes 00 - 03: Image body length
Bytes 04 - 07: Image width in pixels
Bytes 08 - 11: Image height in pixels
Bytes 12 - [12 + image body length - 1]: Image body
Bytes [12 + image body length] - [268 + image body length]: RGB palette (if available)
"""
class PcxItem:
	def __init__(self, fileType, fileBody):
		self.size, self.width, self.height = struct.unpack("3i", fileBody[:12])
		self.image = fileBody[12 : 12 + self.size]
		if fileType == 0x10:
			self.palette = fileBody[12 + self.size : 12 + self.size + 3*256]
			self.image = Image.frombuffer("RGB", (self.width, self.height), self.image, "raw", "P", 0, 1)
			self.image.putpalette(self.palette)
		elif fileType == 0x11:
			self.palette = ''
			image = ''
			for i in range(0, len(self.image), 3):
				image += self.image[i + 2] + self.image[i + 1] + self.image[i]
			self.image = image
			self.image = Image.frombuffer('RGB', (self.width, self.height), self.image, 'raw', 'RGB', 0, 1)
	
	def save(self, dst, filename):
		filename = "%s.png"%filename
		self.image.save(unique.save(dst, filename), "PNG")
