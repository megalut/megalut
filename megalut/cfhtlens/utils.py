"""
Helper functions related to CFHTLenS data.
"""

import os
import glob

import astropy.table
import astropy.wcs

import numpy as np


import logging
logger = logging.getLogger(__name__)



class Pointing():
	"""
	Class to find files related to a CFHTLenS pointing.
	"""

	all_labels = ['W1m0m0', 'W1m0m1', 'W1m0m2', 'W1m0m3', 'W1m0m4', 'W1m0p1', 'W1m0p2', 'W1m0p3', 'W1m1m0', 'W1m1m1', 'W1m1m2', 'W1m1m3', 'W1m1m4', 'W1m1p1', 'W1m1p2', 'W1m1p3', 'W1m2m0', 'W1m2m1', 'W1m2m2', 'W1m2m3', 'W1m2m4', 'W1m2p1', 'W1m2p2', 'W1m2p3', 'W1m3m0', 'W1m3m1', 'W1m3m2', 'W1m3m3', 'W1m3m4', 'W1m3p1', 'W1m3p2', 'W1m3p3', 'W1m4m0', 'W1m4m1', 'W1m4m2', 'W1m4m3', 'W1m4m4', 'W1m4p1', 'W1m4p2', 'W1m4p3', 'W1p1m0', 'W1p1m1', 'W1p1m2', 'W1p1m3', 'W1p1m4', 'W1p1p1', 'W1p1p2', 'W1p1p3', 'W1p2m0', 'W1p2m1', 'W1p2m2', 'W1p2m3', 'W1p2m4', 'W1p2p1', 'W1p2p2', 'W1p2p3', 'W1p3m0', 'W1p3m1', 'W1p3m2', 'W1p3m3', 'W1p3m4', 'W1p3p1', 'W1p3p2', 'W1p3p3', 'W1p4m0', 'W1p4m1', 'W1p4m2', 'W1p4m3', 'W1p4m4', 'W1p4p1', 'W1p4p2', 'W1p4p3', 'W2m0m0', 'W2m0m1', 'W2m0m2', 'W2m0p1', 'W2m0p2', 'W2m0p3', 'W2m1m0', 'W2m1m1', 'W2m1m2', 'W2m1p1', 'W2m1p2', 'W2m1p3', 'W2m2m0', 'W2m2m1', 'W2m2m2', 'W2m2p1', 'W2m2p2', 'W2m2p3', 'W2p1m0', 'W2p1m1', 'W2p1p1', 'W2p1p2', 'W2p1p3', 'W2p2m0', 'W2p2m1', 'W2p2p1', 'W2p2p2', 'W2p2p3', 'W2p3m0', 'W2p3m1', 'W2p3m3', 'W2p3p1', 'W2p3p2', 'W2p3p3', 'W3m0m0', 'W3m0m1', 'W3m0m2', 'W3m0m3', 'W3m0p1', 'W3m0p2', 'W3m0p3', 'W3m1m0', 'W3m1m1', 'W3m1m2', 'W3m1m3', 'W3m1p1', 'W3m1p2', 'W3m1p3', 'W3m2m0', 'W3m2m1', 'W3m2m2', 'W3m2m3', 'W3m2p1', 'W3m2p2', 'W3m2p3', 'W3m3m0', 'W3m3m1', 'W3m3m2', 'W3m3m3', 'W3m3p1', 'W3m3p2', 'W3m3p3', 'W3p1m0', 'W3p1m1', 'W3p1m2', 'W3p1m3', 'W3p1p1', 'W3p1p2', 'W3p1p3', 'W3p2m0', 'W3p2m1', 'W3p2m2', 'W3p2m3', 'W3p2p1', 'W3p2p2', 'W3p2p3', 'W3p3m0', 'W3p3m1', 'W3p3m2', 'W3p3m3', 'W3p3p1', 'W3p3p2', 'W3p3p3', 'W4m0m0', 'W4m0m1', 'W4m0m2', 'W4m0p1', 'W4m1m0', 'W4m1m1', 'W4m1m2', 'W4m1p1', 'W4m1p2', 'W4m1p3', 'W4m2m0', 'W4m2p1', 'W4m2p2', 'W4m2p3', 'W4m3m0', 'W4m3p1', 'W4m3p2', 'W4m3p3', 'W4p1m0', 'W4p1m1', 'W4p1m2', 'W4p1p1', 'W4p2m0', 'W4p2m1', 'W4p2m2']
	good_codes = ['W1m0m0_i', 'W1m0m3_i', 'W1m0m4_y', 'W1m0p1_i', 'W1m0p2_i', 'W1m0p3_i', 'W1m1m0_i', 'W1m1m2_i', 'W1m1m3_i', 'W1m1m4_y', 'W1m1p3_i', 'W1m2m1_i', 'W1m2m2_i', 'W1m2m3_i', 'W1m2p1_i', 'W1m2p2_i', 'W1m3m0_i', 'W1m3m2_i', 'W1m3m4_y', 'W1m3p1_i', 'W1m3p3_i', 'W1m4m0_i', 'W1m4m1_i', 'W1m4m3_i', 'W1m4m4_y', 'W1m4p1_i', 'W1p1m1_i', 'W1p1m2_i', 'W1p1m3_i', 'W1p1m4_y', 'W1p1p1_y', 'W1p1p2_i', 'W1p1p3_i', 'W1p2m0_i', 'W1p2m2_i', 'W1p2m3_i', 'W1p2m4_y', 'W1p2p1_i', 'W1p2p2_i', 'W1p2p3_i', 'W1p3m1_i', 'W1p3m2_i', 'W1p3m3_i', 'W1p3m4_y', 'W1p3p1_y', 'W1p3p2_i', 'W1p3p3_i', 'W1p4m0_i', 'W1p4m1_i', 'W1p4m2_i', 'W1p4m3_i', 'W1p4m4_y', 'W1p4p1_i', 'W1p4p2_i', 'W1p4p3_i', 'W2m0m0_i', 'W2m0m1_i', 'W2m0p1_i', 'W2m0p2_i', 'W2m1m0_i', 'W2m1m1_i', 'W2m1p1_i', 'W2m1p3_i', 'W2p1m0_i', 'W2p1p1_i', 'W2p1p2_i', 'W2p2m0_i', 'W2p2m1_i', 'W2p2p1_i', 'W2p2p2_i', 'W2p3m0_i', 'W2p3m1_i', 'W2p3p1_i', 'W2p3p3_i', 'W3m0m1_y', 'W3m0m2_i', 'W3m0m3_i', 'W3m0p2_i', 'W3m0p3_i', 'W3m1m0_i', 'W3m1m2_i', 'W3m1m3_i', 'W3m1p1_i', 'W3m1p2_i', 'W3m1p3_i', 'W3m2m1_y', 'W3m2m2_i', 'W3m2m3_i', 'W3m2p1_y', 'W3m2p2_i', 'W3m3m0_i', 'W3m3m1_i', 'W3m3m2_i', 'W3m3m3_i', 'W3m3p1_i', 'W3m3p2_i', 'W3p1m0_i', 'W3p1m1_i', 'W3p1m2_i', 'W3p1m3_i', 'W3p1p2_i', 'W3p1p3_i', 'W3p2m0_i', 'W3p2m3_y', 'W3p2p3_i', 'W3p3m1_i', 'W3p3m3_i', 'W3p3p1_i', 'W3p3p2_i', 'W3p3p3_i', 'W4m0m2_i', 'W4m0p1_i', 'W4m1m0_i', 'W4m1m1_i', 'W4m1m2_i', 'W4m1p1_y', 'W4m2m0_i', 'W4m2p1_i', 'W4m2p3_y', 'W4m3m0_i', 'W4m3p1_i', 'W4m3p2_i', 'W4m3p3_y', 'W4p1m0_i', 'W4p1m1_i', 'W4p1m2_i', 'W4p2m0_i', 'W4p2m1_i', 'W4p2m2_i']
	bad_codes = ['W1m0m1_i', 'W1m0m2_i', 'W1m1m1_i', 'W1m1p1_i', 'W1m1p2_i', 'W1m2m0_i', 'W1m2m4_y', 'W1m2p3_i', 'W1m3m1_i', 'W1m3m3_i', 'W1m3p2_i', 'W1m4m2_i', 'W1m4p2_i', 'W1m4p3_i', 'W1p1m0_i', 'W1p1p1_i', 'W1p2m1_i', 'W1p2p2_y', 'W1p3m0_i', 'W1p3p1_i', 'W1p4p2_y', 'W2m0p3_i', 'W2m1p2_i', 'W2p1m1_i', 'W2p1p1_y', 'W2p1p3_i', 'W2p2p2_y', 'W2p2p3_i', 'W2p3p2_i', 'W3m0m0_i', 'W3m0m1_i', 'W3m0p1_i', 'W3m1m1_i', 'W3m1p3_y', 'W3m2m0_i', 'W3m2m1_i', 'W3m2p1_i', 'W3m2p3_i', 'W3m2p3_y', 'W3m3p1_y', 'W3m3p3_i', 'W3p1p1_i', 'W3p2m1_i', 'W3p2m2_i', 'W3p2m3_i', 'W3p2p1_i', 'W3p2p2_i', 'W3p3m0_i', 'W3p3m1_y', 'W3p3m2_i', 'W3p3m2_y', 'W3p3p2_y', 'W4m0m0_i', 'W4m0m1_i', 'W4m1m1_y', 'W4m1p1_i', 'W4m1p2_y', 'W4m1p3_y', 'W4m2p2_y', 'W4p1p1_i']
	

	def __init__(self, code=None, label="W1m0m0", filtername="i",
		surveydir = "/vol/braid1/vol1/thomas/SHEARCOLLAB/Bonn/",
		swarpconfigpath = "/users/mtewes/CFHTLenS/create_coadd_swarp.swarp",
		catdir = "/vol/fohlen11/fohlen11_1/hendrik/data/CFHTLenS/release_cats/"
		):
		"""
		Usually you just give me a code such as "W1m0m0_i", and don't need to worry about the other params.
		"""
		
		if code is not None:
			self.setcode(code)
		else:
			self.label = label # can be hotchanged...
			self.filtername = filtername # can be hotchanged...
		
		self.surveydir = surveydir
		self.swarpconfigpath = swarpconfigpath
		self.catdir = catdir
	
	def __str__(self):
		return self.getcode()

	def getcode(self):
		return "%s_%s" % (self.label, self.filtername)
		
	def setcode(self, code):
		assert len(code) == 8
		self.label = code[0:6]
		self.filtername = code[7:8]

	def basedir(self):
		return os.path.join(self.surveydir, self.label)

	def datadir(self):
		return os.path.join(self.basedir(), self.filtername, "single_V2.2A")

	def headdir(self):
		return os.path.join(self.basedir(), self.filtername, "headers_V2.2A")

	def psfdir(self):
		return os.path.join(self.basedir(), self.filtername, "lensfit_V2.2A_v7p0p3-beta_origpsfweight/psfs")

	def swarpconfig(self):
		return self.swarpconfigpath

	def explistdir(self):
		#return os.path.join(self.basedir(), self.filtername, "lensfit_V2.2A_v7p1p0-beta_origpsfweight/work")
		return os.path.join(self.basedir(), self.filtername, "lensfit_V2.2A_v7p0p3-beta_origpsfweight/work")
	
	def explists(self):
		filepaths = glob.glob(os.path.join(self.explistdir(), "*.list"))
		return map(lambda x: os.path.splitext(os.path.basename(x))[0], filepaths)

	def catpath(self):
		candidates = sorted(glob.glob(os.path.join(self.catdir, "%s_%s*_release_mask.cat" % (self.label, self.filtername))))
		if len(candidates) != 1:
			logger.critical("Problem with cat identification for %s: %S" % (str(self), candidates))
		return candidates[0]

	def coaddimgpath(self):
		return os.path.join(self.basedir(), self.filtername, "coadd_V2.2A", "%s_%s.V2.2A.swarp.cut.fits" % (self.label, self.filtername))
	
	
	def validate(self):
		"""
		Checks that all these files do indeed exist.
		"""
		for path in [self.basedir(), self.datadir(), self.headdir(), self.swarpconfig(), self.explistdir(), self.catpath(), self.coaddimgpath()]:	
			if not os.path.exists(path):
				logger.warning("Cannot find path %s" % path)
		if len(self.explists()) == 0:
			logger.warning("Can't find expslists for %s" % str(self))

		os.path.exists(self.catpath())
		

	

def readcat(filepath):
	"""
	Custom catalog reader.
	"""
	logger.info("Reading %s..." % (os.path.basename(filepath)))
	return astropy.table.Table.read(filepath, hdu=1) # Despite beeing not documented, this hdu=1 works !



def removejunk(cat):
	"""
	Makes those catalogs a bit smaller by removing some "array" columns
	"""
	
	toremove = [
		"MAG_APER_i", "MAGERR_APER_i", "FLUX_APER_i", "FLUXERR_APER_i",
		"MAG_APER_y", "MAGERR_APER_y", "FLUX_APER_y", "FLUXERR_APER_y",
		"MAG_APER_z", "MAGERR_APER_z", "FLUX_APER_z", "FLUXERR_APER_z",
		"MAG_APER_r", "MAGERR_APER_r", "FLUX_APER_r", "FLUXERR_APER_r",
		"MAG_APER_g", "MAGERR_APER_g", "FLUX_APER_g", "FLUXERR_APER_g",
		"MAG_APER_u", "MAGERR_APER_u", "FLUX_APER_u", "FLUXERR_APER_u",
		"MAG_APER", "MAGERR_APER",
		"PZ_full"
	]
	
	for colname in toremove:
		if colname not in cat.colnames:
			logger.warning("No %s in cat" % (colname))
			continue
		
		cat.remove_column(colname)
	

def stars(cat):
	"""
	Quick and dirty example keeping only stars
	"""

	selector = np.logical_and(cat['weight'] < 0.1, cat['fitclass'] == 1)
	selector = np.logical_and(selector, cat['CLASS_STAR'] > 0.95)
	
	return cat[selector]




def computepos(imgfilepath, cat, alpha="ALPHA_J2000", delta="DELTA_J2000", x="new_x", y="new_y"):
	"""
	I use the fits header WCS to compute the pixel postions of the galaxies in cat.
	Postponed to later...
	"""
	from astropy import wcs

	pass




