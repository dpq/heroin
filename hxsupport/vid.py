#!/usr/bin/python
import struct
import os
import time
import unique

"""
*** VID format ***
Bytes 00 - 03: Number of files in this VID
"""
class VidFile:
	def __init__(self, filename, src, dst):
		file = open(os.path.join(src, filename))
		self.itemCount = struct.unpack("i", file.read(4))[0]
		self.items = []
		for i in range(0, self.itemCount):
			v = VidItem(file)
			if v.filename != "":
				self.items.append(v)
		# We have to calculate file sizes manually, since the format doesn't contain this information
		for i in range(1, len(self.items)):
			self.items[i - 1].size = self.items[i].offset - self.items[i - 1].offset
		self.items[-1].size = os.stat(os.path.join(src, filename))[6] - self.items[-1].offset
		for i in range(0, len(self.items)):
			self.items[i].setBody(file)
			self.items[i].save(dst)
			self.items[i] = None

"""
*** VID item format ***
Bytes 00 - 39 : File name
Bytes 40 - 43 : File body start offset
"""
class VidItem:
	def __init__(self, file):
		self.filename = file.read(40).split('\x00')[0].lower()
		self.offset = struct.unpack("i", file.read(4))[0]
		self.size = 0
	
	def setBody(self, file):
		file.seek(self.offset)
		self.body = file.read(self.size)
	
	def save(self, dst):
		# Make sure the path to save the file is available
		dst = os.path.join(dst, "video")
		if not os.path.isdir(dst):
			try:
				os.makedirs(dst)
			except:
				print "Could not create destination directory", dst
				return
		file = open(unique.save(dst, self.filename), "wb")
		file.write(self.body)
		file.close()
