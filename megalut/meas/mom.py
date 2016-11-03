"""
Simple self-coded moments, for tests and playing around.
In theory, no need for galsim here.
"""

import numpy as np
import copy
from .. import tools
import utils

from datetime import datetime


import astropy
import astropy.table

import logging
logger = logging.getLogger(__name__)




def measfct(cat, runon="img", prefix="mom_", xname="x", yname="y", stampsize=None, **kwargs):
	"""
	
	:param runon: "img" or "psf" or ... -- decides on which image this should run.
		You might want to adjust the prefix accordingly.
	:param prefix: a prefix for the new column names. By default, no prefix is used.
	:param xname: name of the column containing the x center around which to measure
	:param yname: idem for y
		
	"""
	
	
	#img = astropy.io.fits.getdata(cat.meta[runon].filepath) # a 2d numpy array

	# We get the stamp size to use:
	stampsize = cat.meta[runon].get_stampsize(stampsize)

	# We load the image:
	img = cat.meta[runon].load()

	# And we pass it, with all required kwargs, to the lower-level function:
	return measure(img, cat, xname=cat.meta[runon].xname, yname=cat.meta[runon].yname, stampsize=stampsize, **kwargs)



def measure(img, cat, xname="x", yname="y", prefix="mom_", stampsize=None, centroweightsize=None, secondweightsizes=None):
	"""
	Top level function to measure non-adaptive quadrupole (mainly) moments
	
	:param centroweightsize: size of the weight function to use to find the centroid.
		If None, I'll not find the centroid, and use the stamp center instead.
	
	"""

	
	starttime = datetime.now()
	logger.info("Starting measurements on {} stamps...".format(len(cat)))

	if secondweightsizes is None:
		radii = [5]

	if type(img) is str:
		logger.debug("You gave me a filepath, and I'm now loading the image...")
		img = tools.image.loadimg(img)
		
	# We prepare an output table with all the required columns
	output = astropy.table.Table(copy.deepcopy(cat), masked=True) # Convert the table to a masked table
	# A bit strange: reading the doc I feel that this conversion is not needed.
	# But without it, it just doesn't result in a masked table once the masked columns are appended.
	
	# Pepare the list of new columns 
	colnames = ["x", "y", "flag"]
	for c in ["e1", "e2", "r", "qxx", "qyy", "qxy"]:	
		colnames.extend(["{}{}".format(c, secondweightsize) for secondweightsize in secondweightsizes])
	if len(list(set(colnames))) != 3+6*len(secondweightsizes):
		raise RuntimeError("Problem with secondweightsizes names!")
	utils.add_new_cols(output, prefix=prefix, floatcols=colnames, boolcols=None)
		
	# Get a MomentEngine
	me = MomentEngine(stampsize=stampsize)
	
	
	# And loop
	for gal in output:
		
		if gal.index%1000 == 0:
			logger.info("%6.2f%% done (%i/%i) " % (100.0*float(gal.index)/float(len(cat)), gal.index, len(cat)))
		
		(x, y) = (gal[xname], gal[yname])
		(gps, flag) = tools.image.getstamp(x, y, img, stampsize)
		
		if flag != 0:
			logger.debug("Galaxy not fully within image:\n %s" % (str(gal)))
			gal[prefix+"flag"] = flag
			continue

		array = gps.array.transpose()
		assert array.shape == (stampsize, stampsize)
		
		# First, we need a center to place the weight function:
		
		if centroweightsize == None:
			centro = (me.xcenter, me.ycenter)
			
		else:
			# Finding the centroid, with a weighting function centered on the stamp center:
			weights = me.make_weights(func="Gauss", center=None, sigma=centroweightsize)
			
			centro = me.measure_first_moments(weights*array)
			# Checking it:
			#print centro[0], me.xcenter, centro[1], me.ycenter
			
			if np.hypot(centro[0]-me.xcenter, centro[1]-me.ycenter) >= centroweightsize:
				logger.info("Centroid failed for galaxy %i" % (gal.index))
				gal[prefix+"flag"] = 10
				continue
		
		gal[prefix + "x"] = centro[0] # Arg, to turn this into absolute again, would add x, but then what happens if x is float is bad!!!! Careful
		gal[prefix + "y"] = centro[1]
		
		# Ready to measure the second moments
		for secondweightsize in secondweightsizes:
			
			# We build the centered weight function
			weights = me.make_weights(func="Gauss", center=centro, sigma=secondweightsize)
			# And measure moments
			(qxx, qyy, qxy) = me.measure_second_moments(weights*array, center=centro)
			
			gal[prefix + "qxx{}".format(secondweightsize)] = qxx
			gal[prefix + "qyy{}".format(secondweightsize)] = qyy
			gal[prefix + "qxy{}".format(secondweightsize)] = qxy
			
	
			# And convert this to ellipses
			try:	
				(e1, e2, r) = me.compute_ellipse((qxx, qyy, qxy))
				gal[prefix + "e1{}".format(secondweightsize)] = e1
				gal[prefix + "e2{}".format(secondweightsize)] = e2
				gal[prefix + "r{}".format(secondweightsize)] = r
			
			except ValueError:
				logger.info("Ellipse params failed for galaxy %i" % (gal.index))
				gal[prefix+"flag"] = 20
				continue
		
	nfailed = np.sum(output[prefix + "flag"] >= 10)
	if nfailed != 0:
		logger.warning("The moment computation failed on %i out of %i sources (%.1f percent)" % (nfailed, len(cat), 100.0*float(nfailed)/float(len(cat))))


	return output



class MomentEngine:
	"""Measures moments on square stamps.
	A MomentEngine object allows you to measure moments on many stamps.
	
	The normal procedure:
	- measure first moments using a relatively wide gaussian weight function centered on the stamp center
	- measure central second moments, centered 
	
	"""
	def __init__(self, stampsize):
		self.stampsize = stampsize

		self.make_pos()


	def make_pos(self):
		"""Prepares x and y position arrays and stamp centers, as we'll keep reusing them.
		"""
		(self.xes, self.yes) = np.mgrid[0:self.stampsize, 0:self.stampsize] + 1.0 # The value of the first pixel goes with coordinates (1.0, 1.0). That's our convention.
		(self.xcenter, self.ycenter) = ((self.stampsize/2.0 + 0.5), (self.stampsize/2.0 + 0.5)) # Consistent with this convention.


	def make_weights(self, func="flat", center=None, sigma=None):
		"""Builds an array of weights
		"""
		if func is "flat":
			weights = np.ones((stampsize, stampsize), dtype=float)

		elif func is  "Gauss":
		
			if center is None:
				center = (self.xcenter, self.ycenter) # Use the stamp center
				
			centerdists	= np.hypot(self.xes - center[0], self.yes - center[1])
			weights = np.exp((-1.0 * centerdists**2) / (2.0 * sigma**2))
			
		else:
			raise RuntimeError("Unknown func")

		assert weights.shape == (self.stampsize, self.stampsize)
		return weights
		

	def measure_first_moments(self, array, sumarray=None):
		"""Plain measurement of first moments on a 2D numpy array
		"""
		assert array.shape == (self.stampsize, self.stampsize)
		
		if sumarray == None:
			sumarray = np.sum(array)
			
		x = np.sum(self.xes * array) / sumarray
		y = np.sum(self.yes * array) / sumarray

		return (x, y)


	def measure_second_moments(self, array, sumarray=None, center=None):
		"""Plain measurement of central second moments on a 2D numpy array.
		"""
		assert array.shape == (self.stampsize, self.stampsize)
	
		if sumarray == None:
			sumarray = np.sum(array)
		if center is None:
			center = (self.xcenter, self.ycenter) # Use the stamp center
		
		qxx = np.sum(array * (self.xes - center[0])**2) / sumarray
		qyy = np.sum(array * (self.yes - center[1])**2) / sumarray
		qxy = np.sum(array * (self.xes - center[0]) * (self.yes - center[1])) / sumarray

		return (qxx, qyy, qxy)


	def compute_ellipse(self, second_moments):
		"""Turns a tuple of second moments into (e1, e2, r)
		"""
		
		(qxx, qyy, qxy) = second_moments
		
		qdiff = (qxx * qyy) - qxy**2
		
		if qdiff < 0.0:
			raise ValueError()
		else:
			edenum = qxx + qyy + 2.0*np.sqrt(qdiff)
			e1 = (qxx - qyy) / edenum
			e2 = 2.0 * qxy / edenum
			# and 
			r = np.sqrt(qxx**2 + qyy**2)
			return (e1, e2, r)
			
		
		
	
#def measfct(cat, runon="img", prefix="mom_", xname="x", yname="y", stampsize=100):
#	"""
#	
#	:param runon: "img" or "psf" or ... -- decides on which image this should run.
#		You might want to adjust the prefix accordingly.
#	:param prefix: a prefix for the new column names. By default, no prefix is used.
#	:param xname: name of the column containing the x center around which to measure
#	:param yname: idem for y
#		
#	"""
#	
#	
#	#img = astropy.io.fits.getdata(cat.meta[runon].filepath) # a 2d numpy array
#	
#	# We load the image:
#	img = cat.meta[runon].load()
#
#
#	# Prepare the catalog: THIS SHOULD BE REVIEWED ONCE WE ALL ADOPT ASTROPY 1.0 AND A RECENT NUMPY !
#	cat = astropy.table.Table(copy.deepcopy(cat), masked=True) # Convert the table to a masked table
#	# A bit stange: reading the doc I feel that this conversion is not needed.
#	# But without it, it just doesn't result in a masked table once the masked columns are appended.
#
#	cat.add_columns([
#		astropy.table.MaskedColumn(name=prefix+"x", dtype=float, length=len(cat)),
#		astropy.table.MaskedColumn(name=prefix+"y", dtype=float, length=len(cat)),
#		astropy.table.MaskedColumn(name=prefix+"e1", dtype=float, length=len(cat)),
#		astropy.table.MaskedColumn(name=prefix+"e2", dtype=float, length=len(cat)),
#		astropy.table.MaskedColumn(name=prefix+"r", dtype=float, length=len(cat)),
#		astropy.table.MaskedColumn(name=prefix+"flag", dtype=float, length=len(cat)),
#	])
#	for col in ["x", "y", "e1", "e2", "r", "flag"]:
#		cat[prefix+col].mask = [True] * len(cat)
#	
#	
#	
#	# Preparing a weight function, and some often reused terms
#	
#	(xes, yes) = np.mgrid[0:stampsize, 0:stampsize] + 1.0 # The value of the first pixel goes with coordinates (1, 1). That's our convention.
#	weights = np.ones((stampsize, stampsize), dtype=float)
#	centerdists = np.hypot((xes - (stampsize/2.0 + 0.5)), (yes - (stampsize/2.0 + 0.5)))
#	sigma = 5
#	weights = np.exp((-1.0 * centerdists**2) / (2.0 * sigma**2))
#	
#	
#	# And now the loop
#	for gal in cat:
#		
#		# Some simplistic progress indication:
#		if gal.index%1000 == 0:
#			logger.info("%6.2f%% done (%i/%i) " % (100.0*float(gal.index)/float(len(cat)), gal.index, len(cat)))
#		
#		(x, y) = (gal[cat.meta[runon].xname], gal[cat.meta[runon].yname])
#		(gps, flag) = tools.image.getstamp(x, y, img, stampsize)
#		
#		if flag != 0:
#			logger.debug("Galaxy not fully within image:\n %s" % (str(gal)))
#			gal[prefix+"flag"] = flag
#			continue
#		
#		else:
#			
#			array = gps.array.transpose()
#			array *= weights
#			#array = weights
#			#print array.shape
#			
#			assert array.shape == (stampsize, stampsize)
#			
#			sumarray = np.sum(array)
#				
#			xmean = np.sum(xes * array) / sumarray
#			ymean = np.sum(yes * array) / sumarray
#			
#			qxx = np.sum(array * (xes - xmean)**2) / sumarray
#			qyy = np.sum(array * (yes - ymean)**2) / sumarray
#			qxy = np.sum(array * (xes - xmean) * (yes - ymean)) / sumarray
#			
#			
#			# Following the GREAT8 handbook...
#			
#			if ((qxx * qyy) - qxy**2) < 0.0:
#				gal[prefix+"flag"] = 10
#				continue
#				
#			edenum = qxx + qyy + 2.0*np.sqrt((qxx * qyy) - qxy**2)
#			e1 = (qxx - qyy) / edenum
#			e2 = 2.0 * qxy / edenum
#			
#			# and 
#	
#			r = np.sqrt(qxx**2 + qyy**2)
#			
#			
#			xmean -= (stampsize/2.0 + 0.5) # The centroid, in relative pixels
#			ymean -= (stampsize/2.0 + 0.5)
#			
#			gal[prefix + "x"] = xmean # Arg, to turn this into absolute again, would add x, but then what happens if x is float is bad!!!! Careful
#			gal[prefix + "y"] = ymean
#			gal[prefix + "e1"] = e1
#			gal[prefix + "e2"] = e2
#			gal[prefix + "r"] = r
#			
#	nfailed = np.sum(cat[prefix + "flag"] >= 10)
#	if nfailed != 0:
#		logger.warning("The moment computation failed on %i out of %i sources (%.1f percent)" % (nfailed, len(cat), 100.0*float(nfailed)/float(len(cat))))
#
#	
#	return cat
#	
