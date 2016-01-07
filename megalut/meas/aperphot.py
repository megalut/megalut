"""
Pure-python aperture photometry, using astropy photutils
The motivation here is to get a central surface brightness in a very direct way, i.e. without first estimating the total size and flux.
"""

import numpy as np

import photutils

import astropy.table
import copy

import logging
logger = logging.getLogger(__name__)

def measfct(cat, runon="img", prefix="aperphot_", xname="adamom_x", yname="adamom_y", radii=None):
	"""
	
	:param runon: "img" or "psf" or ... -- decides on which image this should run.
		You might want to adjust the prefix accordingly.
	:param prefix: a prefix for the new column names. By default, no prefix is used.
	:param xname: name of the column containing the x center around which to measure
	:param yname: idem for y
	:param radii: list of radii of the apertures to use, preferably list of ints.
	
	
	"""
	
	if radii is None:
		radii = [3]

	# Load the image:
	img = cat.meta[runon].load()
	
	# Prepare the catalog: THIS SHOULD BE REVIEWED ONCE WE ALL ADOPT ASTROPY 1.0 AND A RECENT NUMPY !
	cat = astropy.table.Table(copy.deepcopy(cat), masked=True) # Convert the table to a masked table
	# A bit stange: reading the doc I feel that this conversion is not needed.
	# But without it, it just doesn't result in a masked table once the masked columns are appended.

	
	colnames = [prefix+"sb{}".format(r) for r in radii]
	if len(list(set(colnames))) != len(radii):
		raise RuntimeError("Problem with radii names!")
	cols = [astropy.table.MaskedColumn(name=colname, dtype=float, length=len(cat)) for colname in colnames]
	cat.add_columns(cols)
	
	for col in colnames:
		cat[col].mask = [True] * len(cat) # Start with everything masked
	
	# We don't even need a loop over objects, cool.
	
	# photutils does not nicely handle masked catalogs.
	# We only measure apertures around non-masked x and y positions:
	goodpos = np.logical_not(np.logical_or(cat[xname].mask, cat[yname].mask))
	assert len(goodpos) == len(cat)
	logger.info("{}/{} positions can be measured.".format(np.sum(goodpos), len(cat)))
	
	# the photuils pixel coordinate convention is described here:
	#http://photutils.readthedocs.org/en/latest/photutils/overview.html#coordinate-conventions
	
	data = img.array # It seems that this orientation is fine
	positions = [(row[xname]-1.0, row[yname]-1.0) for row in cat[goodpos]] # Be careful: we adapt here to the photutils coordinate convention!
	
	for (colname, rad) in zip(colnames, radii):
	
		logger.info("Measuring in apertues of {} pixels...".format(rad))
		apertures = photutils.CircularAperture(positions, r=float(rad))
		photcat = astropy.table.Table(photutils.aperture_photometry(data, apertures), masked=True)
		assert len(photcat) == len(cat[goodpos])
		# We mask nan values: (nan values happend when the aperture is completely out of the array...)
		photcat["aperture_sum"].mask = np.isnan(photcat["aperture_sum"])
		
		cat[colname][goodpos] = photcat["aperture_sum"] / (np.pi * rad**2)
		
		logger.warning("The surface brightness of apertures on the edges of the image is currently wrong!")
		# Trick to implement this well, if needed: run the phot on an array of ones to get the aperture areas.
	
	

	return cat





