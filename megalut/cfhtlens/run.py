"""
A Run class to run MegaLUT. Let's see how this evolves.
All steps are independent
"""
import sys, os
import utils
from .. import utils as megalututils
from .. import gsutils
from .. import meas

import lensfitpsf

import logging
logger = logging.getLogger(__name__)


class Run():

	def __init__(self, pointing,
		basedir = "/vol/fohlen11/fohlen11_1/mtewes/CFHTLenS/megalut/basedir"
		):
		
		self.pointing = pointing
		self.basedir = basedir
		self.workdir = os.path.join(self.basedir, self.pointing.getcode())
		
		if not os.path.exists(self.workdir):
			os.makedirs(self.workdir)

		
		self.psfworkdir = os.path.join(self.workdir, "psf")
		self.psfgrid = os.path.join(self.psfworkdir, "psfgrid.fits")
		
		self.inputcat = os.path.join(self.workdir, "inputcat.pkl")
		self.inputcatmini = os.path.join(self.workdir, "inputcatmini.pkl")
		#self.meascat = os.path.join(self.workdir, "meascat.pkl")
		self.psfcat = os.path.join(self.workdir, "psfcat.pkl")
		self.psfcatmeas = os.path.join(self.workdir, "psfcatmeas.pkl")
		
		

	def prepcat(self):
		"""
		Reads and cleans the CFHTLenS catalog, prepares input for next methods
		"""
		
		cat = utils.readcat(self.pointing.catpath())
		utils.removejunk(cat)
		
		megalututils.writepickle(cat, self.inputcat)

		#cat.keep_columns(["ALPHA_J2000", "DELTA_J2000", "Xpos", "Ypos", "CLASS_STAR", "fitclass", "SeqNr", "FWHM_IMAGE", 'weight', 'fitclass', 'scalelength', 'bulge-fraction', 'model-flux', 'SNratio', 'fit-probability', 'PSF-e1', 'PSF-e2', 'PSF-Strehl-ratio', 'e1', 'e2'])
		
		cat.keep_columns(["ALPHA_J2000", "DELTA_J2000", "Xpos", "Ypos", "SeqNr"])
		
		sqnrs = list(cat["SeqNr"])
		assert len(set(sqnrs)) == len(sqnrs)

		megalututils.writepickle(cat, self.inputcatmini)


	def makepsfstamps(self):
		"""
		Creates the PSF grid images and a catalog telling which PSF to use for which galaxy.
		"""
		cat = megalututils.readpickle(self.inputcatmini)
		
		lensfitpsf.makeexppsfs(cat, self.pointing, workdir = self.psfworkdir)
		cat = lensfitpsf.stackexppsfs(cat, workdir = self.psfworkdir)

		megalututils.writepickle(cat, self.psfcat)

		

	def measpsfstamps(self):
		"""
		Measures the PSF grid
		"""
		
		cat = megalututils.readpickle(self.psfcat)

		img = gsutils.loadimg(self.psfgrid)

		catmeas = meas.galsim_adamom.measure(img, cat, stampsize=32, xname="psfgridx", yname="psfgridy", prefix="psfmes")

		megalututils.writepickle(catmeas, self.psfcatmeas)



