import os
import glob

import astropy.table
import astropy.wcs

import numpy as np


import logging
logger = logging.getLogger(__name__)



class Pointing():
	"""
	A CFHTLenS pointing
	"""


	def __init__(self, label="W1m0m0", filtername="i",
		surveydir = "/vol/braid1/vol1/thomas/SHEARCOLLAB/Bonn/",
		swarpconfigpath = "/users/mtewes/CFHTLenS/create_coadd_swarp.swarp",
		catdir = "/vol/fohlen11/fohlen11_1/hendrik/data/CFHTLenS/release_cats/"
	):
		
		self.surveydir = surveydir
		self.label = label
		self.filtername = filtername # can be hotchanged...
		self.basedir = os.path.join(self.surveydir, self.label)

		self.swarpconfigpath = swarpconfigpath
		self.catdir = catdir
		

	def datadir(self):
		return os.path.join(self.basedir, self.filtername, "single_V2.2A")

	def headdir(self):
		return os.path.join(self.basedir, self.filtername, "headers_V2.2A")

	def psfdir(self):
		return os.path.join(self.basedir, self.filtername, "lensfit_V2.2A_v7p0p3-beta_origpsfweight/psfs")

	def swarpconfig(self):
		return self.swarpconfigpath

	def explistdir(self):
		return os.path.join(self.basedir, self.filtername, "lensfit_V2.2A_v7p1p0-beta_origpsfweight/work")
	
	def explists(self):
		filepaths = glob.glob(os.path.join(self.explistdir(), "*.list"))
		return map(lambda x: os.path.splitext(os.path.basename(x))[0], filepaths)

	def catpath(self):
		"""
		FIX ME, I'm working on this.
		"""
		
		candidates = sorted(glob.glob(os.path.join(self.catdir, "%s_*_release_mask.cat" % (self.label))))
		assert len(candidates) == 1
		return candidates[0]
		

def readcat(filepath):
	"""
	
	"""
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
	"""
	from astropy import wcs

	pass




