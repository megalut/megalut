import os
import f2n
import glob
import megalut
import random
import math
import numpy as np

"""
This is a standalone script example.
To use it, copy it somewhere into your own stuff, change the settings below, and run it !
"""



run = megalut.great3.run.Run(
	datadir = "/vol/fohlen11/fohlen11_1/mtewes/GREAT3/",
	workdir = "/vol/fohlen11/fohlen11_1/mtewes/MegaLUT_GREAT3/",
	branch = ["real_galaxy", "ground", "constant"],
	version = "v0"

)


s = run.gets()

prevpsf = np.zeros((s, s))

lines = []

for subfield in range(0,200,1):
	
	print "Working on subfield %i" % (subfield)
	
	line = []
	psfpath = run.obspsfimgfilepath(subfield=subfield, epoch=0)
	
	psf = megalut.utils.fromfits(psfpath)[0:s,0:s]
	
	img = f2n.f2nimage(numpyarray=psf, verbose=False)
	img.setzscale(0.0, 0.03)
	img.makepilimage("clog", negative = False)
	img.upsample(4)
	
	txt = [
		"Subfield %i" % (subfield)
	]
		
	img.writeinfo(txt, colour=0)
	line.append(img)
	
	diff = psf - prevpsf
	img = f2n.f2nimage(numpyarray=diff, verbose=False)
	img.setzscale(-0.001, 0.001)
	img.makepilimage("lin", negative = False)
	img.upsample(4)
	
	txt = [
		"Diff to prev."
	]
		
	img.writeinfo(txt, colour=0)
	
	
	line.append(img)
	
	lines.append(line)
	prevpsf = psf
	
	
f2n.compose(lines, "psfs.png")
