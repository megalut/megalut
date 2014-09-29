"""
gsutils stands for GalSim utils: often-used GalSim function wrappers, defining conventions.

"""



import os
import galsim

import numpy as np
import logging

logger = logging.getLogger(__name__)


def loadimg(imgfilepath):
	"""
	Uses GalSim to load and image from a FITS file, enforcing that the GalSim origin is (0, 0).
	
	:param imgfilepath: path to FITS image
	:returns: galsim image
	"""
	
	logger.info("Loading FITS image %s..." % (os.path.basename(imgfilepath)))
	img = galsim.fits.read(imgfilepath)
	img.setOrigin(0,0)
	logger.info("Done with loading %s, shape is %s" % (os.path.basename(imgfilepath), img.array.shape))
	
	logger.warning("The origin and stampsize conventions are new and should be tested !")
	
	img.origimgfilepath = imgfilepath # Just to keep this somewhere
	
	return img



def getstamp(x, y, img, stampsize):
	"""
	I prepare a bounded galsim image stamp "centered" at position (x, y) of your input galsim image.
	You can use the array attribute of the stamp if you want to get the actual pixels.
	
	This assumes that the origin of bigimg is set to (0, 0) as done by loadimg()
	(This is the default for GalSim, but not for GREAT3 if I remember well).
	
	:param x: x position of the stamp "center" (i.e., the object), in pixels.
	:param y: 
	:param img: The galsim.Image object from which I should extract the stamp
	:param stampsize: width = height of the stamp, in pixels. Has to be even. 
	
	:returns: a tuple(stamp, flag). Flag is 1 if the stamp could not be extracted, 0 otherwise.
	"""

	
	#assert img.origin() == (0, 0) # This would be nice, but is only available in newer GalSims...
	assert img.xmin == 0 and img.ymin == 0
	assert int(stampsize)%2 == 0 # checking that it's even

	xmin = int(np.round(x - 0.5)) - int(stampsize)/2
	xmax = int(np.round(x - 0.5)) + int(stampsize)/2 - 1
	ymin = int(np.round(y - 0.5)) - int(stampsize)/2
	ymax = int(np.round(y - 0.5)) + int(stampsize)/2 - 1
			
	assert ymax - ymin == stampsize - 1 # This is the GalSim convention, both extermas are "included" in the bounds.
	assert xmax - xmin == stampsize - 1
	
	# We check that these bounds are fully within the image
	if xmin < img.getXMin() or xmax > img.getXMax() or ymin < img.getYMin() or ymax > img.getYMax():
		return (None, 1) # Ugly, should maybe be implemented as raising an exception caught higher up!
		
	# We prepare the stamp
	bounds = galsim.BoundsI(xmin, xmax, ymin, ymax)
	stamp = img[bounds] # galaxy postage stamp
	assert stamp.array.shape == (stampsize, stampsize)
	
	return (stamp, 0)
