#!/usr/bin/python
import struct
import os

"""
*** SND format ***
Bytes 00 - 03: Number of files in this SND
"""
class SndFile:
	def __init__(self, filename, src):
		file = open(os.path.join(src, filename))
		(self.itemCount, ) = struct.unpack("i", file.read(4))
		self.items = []
		for i in range(0, self.itemCount):
			s = SndItem(file)
			if s.filename != "":
				self.items.append(s)
		for i in range(0, len(self.items)):
			self.items[i].setBody(file)

	def save(self, dst):
		for i in range(0, len(self.items)):
			self.items[i].save(dst)

"""
*** SND item format ***
Bytes 00 - 39 : File name
Bytes 40 - 43 : File body start offset
Bytes 44 - 47 : File body size
"""
class SndItem:
	def __init__(self, file):
		self.filename = file.read(40).split('\x00')[0].lower() + ".wav"
		self.offset, self.size = struct.unpack("2i", file.read(8))
	
	def setBody(self, file):
		file.seek(self.offset)
		self.body = file.read(self.size)
	
	def save(self, dst):
		# Make sure the path to save the file is available
		dst = os.path.join(dst, "sound")
		if not os.path.isdir(dst):
			try:
				os.makedirs(dst)
			except:
				print "Could not create destination directory", dst
				return
		dst = os.path.join(dst, self.filename)
		file = open(dst, "wb")
		file.write(self.body)
		file.close()
