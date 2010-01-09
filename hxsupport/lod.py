#!/usr/bin/python
import struct
import os
import time
import unique

"""
*** LOD format ***
Bytes 00 - 03: LOD magic number
Bytes 04 - 07: LOD version number
Bytes 08 - 11: Number of files in this LOD
Bytes 12 - 91: Unknown
Bytes 92 - 320091: Item headers
"""
class LodFile:
	def __init__(self, filename, src, dst):
		file = open(os.path.join(src, filename))
		self.magic = file.read(4)
		if self.magic != "LOD\x00":
			raise Exception("Not a LOD archive")
		self.version, self.itemCount = struct.unpack("2i", file.read(8))
		# We're not sure what these 80 bytes are responsible for
		file.read(80)
		self.items = []
		for i in range(0, 10000):
			l = LodItem(file)
			if l.filename != "":
				self.items.append(l)
		for i in range(0, len(self.items)):
			self.items[i].setBody(file)
			self.items[i].save(dst)
			self.items[i] = None

import pcxitem
import defitem
import zlib

"""
*** LOD item format ***
Bytes 00 - 15: File name, including extension and something unknown
Bytes 16 - 19: File body start offset
Bytes 20 - 23: File body uncompressed size
Bytes 24 - 27: File type
Bytes 28 - 31: File body compressed size
"""
class LodItem:
	def __init__(self, file):
		self.filename = file.read(16).split('\x00')[0].lower()
		self.offset, self.sizeUncompressed, self.fileType, self.sizeCompressed = struct.unpack("4i", file.read(16))
		self.body = ""
		self.output = None
	
	def setBody(self, file):
		file.seek(self.offset)
		# Uncompressed files have a zero compressed size
		if self.sizeCompressed == 0:
			self.body = file.read(self.sizeUncompressed)
		else:
			self.body = zlib.decompress(file.read(self.sizeCompressed))
		# If there is a registered class to process this file type, instantiate the corresponding processing class
		if self.fileType in self.processors.keys():
			self.output = self.processors[self.fileType](self.fileType, self.body)
			# DEF files have their type specified in their own header. This type value is prevalent over the type specified in the LOD item header.
			if self.fileType >= 0x40 and self.fileType <= 0x49:
				self.fileType = self.output.fileType
	
	def save(self, dst):
		# Make sure the path to save the file is available
		dst = os.path.join(dst, self.directories[self.fileType])
		if not os.path.isdir(dst):
			try:
				os.makedirs(dst)
			except:
				print "Could not create destination directory", dst
				return
		# If the file has a special processor, order it to save the file as it sees fit. Otherwise, save the binary dump of the body.
		if self.output:
			self.output.save(dst, self.filename)
		else:
			file = open(unique.save(dst, self.filename), "wb")
			file.write(self.body)
			file.close()

	# Processor classes corresponding to each file type
	processors = {
		0x10: pcxitem.PcxItem,
		0x11: pcxitem.PcxItem,
		0x40: defitem.DefItem,
		0x41: defitem.DefItem,
		0x42: defitem.DefItem,
		0x43: defitem.DefItem,
		0x44: defitem.DefItem,
		0x45: defitem.DefItem,
		0x46: defitem.DefItem,
		0x47: defitem.DefItem,
		0x49: defitem.DefItem,
	}

	# Directories to which to save each file type
	directories = {
		0x01: "campaigns",
		0x02: "txt",
		0x10: "pcx_palette",
		0x11: "pcx_rgb",
		0x40: "combat_spells",
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
