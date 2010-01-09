#!/usr/bin/python
import os

def save(dst, filename):
	path = os.path.join(dst, filename)
	filename = filename.split(".")
	name, ext = ".".join(filename[:-1]), filename[-1]
	i = 0
	while os.path.exists(path):
		print path, ": file exists"
		path = os.path.join(dst, name + ".%d."%i + ext)
		i += 1
	print "Saving ", path
	return path
