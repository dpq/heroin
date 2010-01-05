#!/usr/bin/python
from struct import unpack
import os
"""
*** LOD format ***
Bytes 00 - 03: LOD magic number
Bytes 04 - 07: LOD version number
Bytes 08 - 11: Number of files in this LOD
Bytes 12 - 91: Empty or unknown, depending on the LOD version (200 or 500)
Bytes 92 - 320091: Item headers
"""
class LodFile:
	def __init__(self, filename, src):
		file = open(os.path.join(src, filename))
		self.magic = file.read(4)
		if self.magic != "LOD\x00":
			raise Exception("Not a LOD archive")
		self.version, self.itemCount = unpack("2i", file.read(8))
		self.unknown = file.read(80)
		self.items = []
		for i in range(0, 10000):
			l = LodItem(file)
			if l.filename != "":
				self.items.append(l)
				print l.filename
		for i in range(0, len(self.items)):
			self.items[i].setBody(file)

	def save(self, dst):
		for i in range(0, len(self.items)):
			self.items[i].save(dst)

import pcx

"""
*** LOD item (file header) format ***
Bytes 00 - 15: File name, including extension and something unknown
Bytes 16 - 19: File body start offset
Bytes 20 - 23: File body uncompressed size
Bytes 24 - 27: File type
Bytes 28 - 31: File body compressed size
"""
from zlib import decompress
class LodItem:
	def __init__(self, file):
		self.filename = file.read(16).split('\x00')[0].lower()
		self.offset, self.sizeUncompressed, self.fileType, self.sizeCompressed = unpack("4i", file.read(16))
		self.body = ""
		self.output = None
	
	def setBody(self, file):
		file.seek(self.offset)
		if self.sizeCompressed == 0:
			self.body = file.read(self.sizeUncompressed)
		else:
			self.body = decompress(file.read(self.sizeCompressed))
		if self.fileType in self.classes.keys():
			self.output = self.classes[self.fileType](self.fileType, self.body)
	
	def save(self, dst):
		dst = os.path.join(dst, self.types[self.fileType])
		if not os.path.isdir(dst):
			try:
				os.makedirs(dst)
			except:
				print "Could not create destination directory", dst
				return
		dst = os.path.join(dst, self.filename)
		if self.output:
			if os.path.exists(dst):
				print "Overwriting", dst
			self.output.save(dst)

	classes = {
		0x10: pcx.PcxFile,
		0x11: pcx.PcxFile
	}

	types = {
		0x01: "campaigns",
		0x02: "txt",
		0x10: "pcx_palette",
		0x11: "pcx_rgb",
		0x40: "combat_spells",
		0x41:	"0x41",
		0x42: "combat_creatures",
		0x43: "advmap_objects",
		0x44: "advmap_heroes",
		0x45: "advmap_tiles",
		0x46: "cursors",
		0x47: "interface",
		0x49: "combat_heroes",
		0x4f: "msk",
		0x50: "fnt",
		0x60: "pal"
	}
