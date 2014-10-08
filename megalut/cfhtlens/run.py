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
		
		self.meascat = os.path.join(self.workdir, "meascat.pkl")
		
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

		

	def _meas(self, imgpath, cat, stampsize, xname, yname, sexworkdir):
		"""
		Runs SExtractor and adamom on your stuff
		"""

		# With sex
		
		params = ["VECTOR_ASSOC(3)", "XWIN_IMAGE", "YWIN_IMAGE", "AWIN_IMAGE", "BWIN_IMAGE", "THETAWIN_IMAGE", "FLUX_WIN", "FLUXERR_WIN",
			 "FLUX_AUTO", "FWHM_IMAGE", "BACKGROUND", "FLAGS", "FLAGS_WIN", "NITER_WIN"]
		config = {"BACK_TYPE":"MANUAL", "BACK_VALUE":0.0, "DETECT_MINAREA":6, "DETECT_THRESH":2, "ANALYSIS_THRESH":2,
			"ASSOC_RADIUS":5, "ASSOC_TYPE":"NEAREST"}
		se = meas.sextractor.SExtractor(sexpath="/vol/software/software/astro/sextractor/sextractor-2.19.5/64bit/bin/sex",
			params=params, config=config, workdir=sexworkdir, nice=15)
		
		out = se.run(imgpath, assoc_cat=cat, assoc_xname=xname, assoc_yname=yname, prefix="sex_")
		
		
		# With adamom
		
		img = gsutils.loadimg(imgpath)
		cat = meas.galsim_adamom.measure(img, out["table"], stampsize=stampsize, xname=xname, yname=yname, prefix="adamom_")
		
		
		return cat



	def measpsfstamps(self):
		"""
		Measures the PSF grid
		"""
		
		cat = megalututils.readpickle(self.psfcat)

		img = gsutils.loadimg(self.psfgrid)

		catmeas = meas.galsim_adamom.measure(img, cat, stampsize=32, xname="psfgridx", yname="psfgridy", prefix="psfmes")

		megalututils.writepickle(catmeas, self.psfcatmeas)



	def measobs(self):
		"""
		
		"""
		
		incat = megalututils.readpickle(self.inputcat)
		sexworkdir = os.path.join(self.workdir, "obs_sex")
		imgpath = self.pointing.coaddimgpath()

		meascat = self._meas(imgpath, cat=incat, stampsize=32, xname="Xpos", yname="Ypos", sexworkdir=sexworkdir)
		
		megalututils.writepickle(meascat, self.meascat)
		
		
		#meas.galsim_adamom.pngstampgrid("test.png", img, cat[5000:5100], xname="Xpos", yname="Ypos", stampsize=32, ncols=10, upsample=4, z1="auto", z2="auto")
	


	def drawsims(self):
		"""
		
		"""
		
		
		
		
		
		








