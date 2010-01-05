#!/usr/bin/python
from os import mkdir, listdir
from os.path import isdir
from string import lower
from sys import argv

src = "Data"
dst = "Lod"
if len(argv) > 1:
	src = argv[1]
if len(argv) > 2:
	dst = argv[2]

if not isdir(dst):
	try:
		mkdir(dst)
	except:
		print "Could not create destination directory", dst

try:
	lods = listdir(src)
except:
	print "Could not list source directory directory", src
	exit()

if len(lods) == 0:
	print "Destination directory %s doesn't contain LOD files"%dst
	exit()

from lod import LodFile

for filename in listdir(src):
	if lower(filename).endswith(".lod"):
		lod = LodFile(filename, src)
		lod.save(dst)
