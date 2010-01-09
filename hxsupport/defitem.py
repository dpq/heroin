#!/usr/bin/python
import struct
import os
import Image, ImageDraw
import time
import unique

"""
*** DEF format ***
Bytes 00 - 03: File type
Bytes 04 - 07: Image width in pixels
Bytes 08 - 11: Image height in pixels
Bytes 12 - 15: Number of sequences in this DEF
Bytes 16 - 271: Palette
"""
class DefItem:
	def __init__(self, fileType, fileBody):
		self.fileType, self.width, self.height, self.sequenceCount = struct.unpack("4i", fileBody[:16])
		self.palette = fileBody[16 : 16 + 3*256]
		# We need to pass the offset value by reference, so we encapsulate it into an array object
		offset = [16 + 3*256]
		self.items = []
		for i in range(0, self.sequenceCount):
			s = DefSequence(fileBody, offset)
			s.index = i
			self.items.append(s)
	
	def save(self, dst, filename):
		dst = os.path.join(dst, filename)
		if not os.path.isdir(dst):
			try:
				os.makedirs(dst)
			except:
				print "Could not create destination directory", dst
				return
		for s in self.items:
			s.save(dst, self.width, self.height, self.palette)

"""
*** DEF sequence format ***
Bytes 00 - 03: Sequence index
Bytes 04 - 07: Number of frames in this sequence
Bytes 08 - 15: Unknown
Bytes 16 - [15 + 13*sequence length]: Frame filenames
Bytes [16 + 13*sequence length] - [15 + 13*sequence length + 4*sequence length]: Frame offsets
"""
class DefSequence:
	def __init__(self, file, offset):
		self.items = []
		self.index, self.frameCount = struct.unpack("2i", file[offset[0]:offset[0] + 8])
		offset[0] += 16
		# Load filenames
		filenames = []
		for i in range(0, self.frameCount):
			filenames.append(file[offset[0]:offset[0] + 13].split('\x00')[0].lower())
			offset[0] += 13
		# Load offsets
		offsets = struct.unpack("%di"%self.frameCount, file[offset[0]:offset[0] + 4*self.frameCount])
		# Load file sizes
		sizes = []
		for i in range(0, self.frameCount):
			sizes.append(struct.unpack("i", file[offsets[i]:offsets[i] + 4])[0])
			offset[0] += 4
		# Load file bodies
		bodies = []
		for i in range(0, self.frameCount):
			bodies.append(file[offsets[i]:offsets[i] + 32 + sizes[i]])
		# Construct frame objects
		for i in range(0, self.frameCount):
			f = DefFrame(filenames[i], offsets[i], sizes[i], bodies[i])
			self.items.append(f)
	
	def save(self, dst, width, height, palette):
		dst = os.path.join(dst, str(self.index))
		if not os.path.isdir(dst):
			try:
				os.makedirs(dst)
			except:
				print "Could not create destination directory", dst
				return
		for f in self.items:
			f.save(dst, width, height, palette)

"""
*** DEF frame format ***
Bytes 00 - 03: Frame size
Bytes 04 - 07: Frame type
Bytes 08 - 11: Frame width in pixels
Bytes 12 - 15: Frame height in pixels
Bytes 16 - 19: Image width in pixels
Bytes 20 - 23: Image height in pixels
Bytes 24 - 27: Horizontal offset
Bytes 28 - 31: Vertical offset
"""
class DefFrame:
	def __init__(self, filename, offset, size, body):
		self.filename = filename
		self.offset = offset
		self.size = size
		self.frameSize, self.frameType, self.frameWidth, self.frameHeight, self.imageWidth, self.imageHeight, self.offsetX, self.offsetY = struct.unpack("8i", body[0:32])
		self.body = body[32:32 + self.frameSize]
		# Type 0 is raw indexed image data
		if self.frameType == 0:
			buffer = self.body
		elif self.frameType == 1:
			buffer = self.readFrame1()
		# Type 2 is rarely used and seems to decode fine using type 3
		elif self.frameType == 2:
			buffer = self.readFrame3()
		elif self.frameType == 3:
			buffer = self.readFrame3()
		else:
			raise Exception("Frame type %d not supported"%self.frameType)
		if buffer == None:
			self.image = None
			return
		self.image = Image.new("P", (self.frameWidth, self.frameHeight), 0x00)
		self.image.paste(Image.frombuffer("RGB", (self.imageWidth, self.imageHeight), buffer, "raw", "P", 0, 1), (self.offsetX, self.offsetY))

	def save(self, dst, width, height, palette):
		# This does not match in OVSLOT.def
		if width != self.frameWidth:
			print "Frame width %d does not match def width %d"%(self.frameWidth, width)
		if height != self.frameHeight:
			print "Frame height %d does not match def height %d"%(self.frameHeight, height)
		
		if self.image == None:
			print "Invalid frame"
			return
		
		if not os.path.isdir(dst):
			try:
				os.makedirs(dst)
			except:
				print "Could not create destination directory", dst
				return
		
		if self.filename in ("clrrvr.def", "mudrvr.def", "lavrvr.def", "watrtl.def"):
			specialDef(dst, palette)
		else:
			self.image.putpalette(palette)
			self.image = self.image.convert("RGBA")
			data = self.image.load()
			for x in xrange(self.image.size[0]):
				for y in xrange(self.image.size[1]):
					if data[x, y] == (0, 255, 255, 255):
						data[x, y] = (0, 0, 0, 0)
					elif data[x, y] == (255, 150, 255, 255):
						data[x, y] = (0, 0, 0, 64)
					elif data[x, y] == (255, 151, 255, 255):
						data[x, y] = (0, 0, 0, 64)
					elif data[x, y] == (255, 0, 255, 255):
						data[x, y] = (0, 0, 0, 128)
			self.image.save(unique.save(dst, "%s.png"%self.filename), "PNG")

	def readFrame1(self):
		# This fails for SGTWMTB.def
		try:
			offsets = struct.unpack("%di"%self.imageHeight, self.body[:self.imageHeight*4])
		except:
			print "Cannot read scanline offsets"
			return None
		offsets += (len(self.body),)
		raw = ""
		for i in xrange(len(offsets) - 1):
			line = self.body[offsets[i]: offsets[i + 1]]
			pos = 0
			while pos < len(line):
				# This fails for SGTWMTA.def, SGTWMTB.def
				try:
					count = ord(line[pos + 1]) + 1
				except IndexError:
					print "Cannot read scanline"
					return None
				if ord(line[pos]) is 0xFF:
					raw += line[pos + 2: pos + 2 + count]
					pos += 2 + count
				else:
					raw += line[pos]*count
					pos += 2
		return raw
	
	def readFrame3(self):
		length = self.imageHeight*self.imageWidth/32 # Length of scanline
		# Unsigned short here
		offsets = struct.unpack("%dH"%length, self.body[:length*2])
		offsets += (len(self.body),)
		raw = ""
		for i in xrange(len(offsets) - 1):
			line = self.body[offsets[i]: offsets[i+1]]
			pos = 0
			while pos < len(line):
				count = ord(line[pos])
				if 0x00 <= count <= 0x1F:   # Empty
					raw += '\x00'*(count + 1)
					pos +=1
				elif 0x20 <= count <= 0x3F: # Light shadow
					raw += '\x01'*(count - 31)
					pos +=1
				elif 0x40 <= count <= 0x5F: # Only used in Tshre.def and AvGnoll.def
					raw += '\x02'*(count - 63)
					pos +=1
				elif 0x60 <= count <= 0x7F: # Only used in Tshre.def
					raw += '\x03'*(count - 95)
					pos +=1
				elif 0x80 <= count <= 0x9F: # Strong shadow
					raw += '\x04'*(count - 127)
					pos +=1
				elif 0xA0 <= count <= 0xBF: # Replaced by player color
					raw += '\x05'*(count - 159)
					pos +=1
				elif 0xE0 <= count <= 0xFF: # Normal colors
					raw += line[pos + 1:pos + count - 222]
					pos += count - 222
				else:
					raise Exception("%02X"%count)
		return raw

	def specialInvert(self, width, height, data):
		for x in xrange(width):
			for y in xrange(height):
				if data[x, y] == (0, 255, 255, 255):
					data[x, y] = (0, 0, 0, 0)
	
	def specialSave(self, dst, image, i):
		dst = os.path.join(dst, "%d.png"%i)
		self.image.save(unique.save(dst, "%s.png"%i), "PNG")

	def specialDef(self, dst, palette):
		if self.filename == "clrrvr.def":
			for i in xrange(12):
				self.image.putpalette(palette[:189*3] + palette[201*3 - i*3:201*3] + palette[189*3:201*3 - i*3] + palette[201*3:])
				image = self.image.convert("RGBA")
				data = image.load()
				specialInvert(self.image.size[0], self.image.size[1], data)
				specialSave(dst, image, i)
		elif self.filename == "mudrvr.def":
			for i in xrange(12):
				self.image.putpalette(palette[:228*3] + palette[240*3 - i*3:240*3] + palette[228*3:240*3 - i*3] + palette[240*3:])
				image = self.image.convert("RGBA")
				data = image.load()
				specialInvert(self.image.size[0], self.image.size[1], data)
				specialSave(dst, image, i)
		elif self.filename == "lavrvr.def":
			for i in xrange(9):
				self.image.putpalette(palette[:240*3] + palette[249*3 - i*3:249*3] + palette[240*3:249*3 - i*3] + palette[249*3:])
				image = self.image.convert("RGBA")
				data = image.load()
				specialInvert(self.image.size[0], self.image.size[1], data)
				specialSave(dst, image, i)
		elif self.filename == "watrtl.def":
			for i in xrange(12):
				self.image.putpalette(palette[:229*3] + palette[241*3 - i*3:241*3] + palette[229*3:241*3 - i*3] + palette[241*3:242*3] + palette[254*3 - i*3:254*3] + palette[242*3:254*3 - i*3] + palette[254*3:])
				image = self.image.convert("RGBA")
				specialSave(dst, image, i)
