"""
A Run class to run MegaLUT. Let's see how this evolves.
All steps are independent
"""
import sys, os
import utils
from .. import utils as megalututils
from .. import gsutils
from .. import meas
from .. import sim

import lensfitpsf
import numpy as np

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
		self.psfmeascat = os.path.join(self.workdir, "psfmeascat.pkl")
		
		self.simworkdir = os.path.join(self.workdir, "sim")
		if not os.path.exists(self.simworkdir):
			os.mkdir(self.simworkdir)
		self.simgalcat = os.path.join(self.simworkdir, "simgalcat.pkl")
		self.matchedpsfcat = os.path.join(self.simworkdir, "matchedpsfcat.pkl")
		


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
		Measures the PSF grid. No need for SExtractor I guess.
		"""
		
		incat = megalututils.readpickle(self.psfcat)
		img = gsutils.loadimg(self.psfgrid)
		
		meascat = meas.galsim_adamom.measure(img, incat, stampsize=32, xname="psfgridx", yname="psfgridy", prefix="psf_adamom_")
		
		megalututils.writepickle(meascat, self.psfmeascat)
	
	
	def _meas(self, imgpath, cat, stampsize, xname, yname, sexworkdir, preprefix=""):
		"""
		Runs SExtractor and adamom on your stuff
		
		:param preprefix: is added before the (fixed) prefix of sex and adamom. Useful when running on PSFs instead of galaxies ?
		"""

		# With sex
		
		params = ["VECTOR_ASSOC(3)", "XWIN_IMAGE", "YWIN_IMAGE", "AWIN_IMAGE", "BWIN_IMAGE", "THETAWIN_IMAGE", "FLUX_WIN", "FLUXERR_WIN",
			 "FLUX_AUTO", "FWHM_IMAGE", "BACKGROUND", "FLAGS", "FLAGS_WIN", "NITER_WIN"]
		config = {"BACK_TYPE":"MANUAL", "BACK_VALUE":0.0, "DETECT_MINAREA":6, "DETECT_THRESH":2, "ANALYSIS_THRESH":2,
			"ASSOC_RADIUS":5, "ASSOC_TYPE":"NEAREST"}
		se = meas.sextractor.SExtractor(sexpath="/vol/software/software/astro/sextractor/sextractor-2.19.5/64bit/bin/sex",
			params=params, config=config, workdir=sexworkdir, nice=15)
		out = se.run(imgpath, assoc_cat=cat, assoc_xname=xname, assoc_yname=yname, prefix=preprefix+"sex_")
		
		
		# With adamom
		
		img = gsutils.loadimg(imgpath)
		cat = meas.galsim_adamom.measure(img, out["table"], stampsize=stampsize, xname=xname, yname=yname, prefix=preprefix+"adamom_")
		
		return cat

	def _calcsex(self, cat):	
		"""
		I calculate some new columns based on the SExtractor output
		These columns are meant to be efficient ML  features.
		
		- g1
		- g2
		
		"""



	def measobs(self):
		"""
		Runs _meas on the observations
		"""
		
		imgpath = self.pointing.coaddimgpath()
		incat = megalututils.readpickle(self.inputcat)
		sexworkdir = os.path.join(self.workdir, "obs_sex")
		
		meascat = self._meas(imgpath, cat=incat, stampsize=32, xname="Xpos", yname="Ypos", sexworkdir=sexworkdir)
		
		megalututils.writepickle(meascat, self.meascat)
		
		
		#meas.galsim_adamom.pngstampgrid("test.png", img, cat[5000:5100], xname="Xpos", yname="Ypos", stampsize=32, ncols=10, upsample=4, z1="auto", z2="auto")
	


	def drawsims(self):
		"""
		
		"""
		
		n_sim = 20
		n_realizations = 3
		
		class MySimParams(sim.params.Params):
			def get_flux(self):
				return 600.0
		mysimparams = MySimParams()

		simgalcat = sim.stampgrid.drawcat(mysimparams, n=n_sim, stampsize=32)
		megalututils.writepickle(simgalcat, self.simgalcat)
		

		psfimg = gsutils.loadimg(self.psfgrid)
		psfcat = megalututils.readpickle(self.psfmeascat)
		psfcat.meta["stampsize"] = 32

		# We randomly draw PSFs to go with our simgals:
		matchedpsfcat = psfcat[np.random.randint(low=0, high=len(psfcat), size=len(simgalcat))]
		megalututils.writepickle(matchedpsfcat, self.matchedpsfcat)
		
		# And we start writing the simulations

		for i in range(n_realizations):
			
			logger.info("Making realization %i..." % (i))
			sim.stampgrid.drawimg(simgalcat, psfcat=matchedpsfcat, psfimg=psfimg,
				psfxname="psfgridx", psfyname="psfgridy",
				simgalimgfilepath=os.path.join(self.simworkdir, "%03i_simgalimg.fits" % (i)),
				simtrugalimgfilepath=os.path.join(self.simworkdir, "%03i_simtrugalimg.fits" % (i)),
				simpsfimgfilepath=os.path.join(self.simworkdir, "%03i_simpsfimg.fits" % (i))
			)
	

	
		
		








