#!/usr/bin/python
from os import mkdir, listdir
from os.path import isdir
from string import lower
from sys import argv

src = "Data"
if len(argv) > 1:
	src = argv[1]

try:
	lods = listdir(src)
except:
	print "Could not list source directory directory", src
	exit()

from lod import LodFile
from snd import SndFile
from vid import VidFile

for filename in listdir(src):
	if lower(filename).endswith(".lod"):
		lod = LodFile(filename, src, "Lod")
	elif lower(filename).endswith(".snd"):
		snd = SndFile(filename, src, "Snd")
	elif lower(filename).endswith(".vid"):
		vid = VidFile(filename, src, "Vid")
