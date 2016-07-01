"""
Quick and dirty GREAT3 Run class making use of the new code of branch #73
"""

import logging
logger = logging.getLogger(__name__)

import os
import astropy
import numpy as np

import utils
import io
from megalut import sim
from megalut import tools
from megalut import learn
from megalut import meas

import copy
import glob
import shutil

class Run(utils.Branch):
	
	def __init__(self, experiment, obstype, sheartype, datadir=None, workdir=None,\
				  subfields=range(200)):
		
		utils.Branch.__init__(self, experiment, obstype, sheartype, datadir, workdir)
		logger.info("Working on branch %s-%s-%s" % (experiment, obstype, sheartype))

		self._mkdir(workdir)
		self.subfields=subfields
		
		# This is **way** too "magic" and weird. For now let's just use "self.subfields"
		
		#if self.sheartype == "constant":
		#	self.simsubfields = subfields
		#elif self.sheartype == "variable":
		#	self.simsubfields = np.asarray(subfields)/20.
		#	self.simsubfields=self.simsubfields.astype(np.int)
		#	self.simsubfields *= 20
		#	self.simsubfields = np.unique(self.simsubfields)

		
	def _mkdir(self, workdir):
		"""
		Creates the working directories. Outputs a warning if the directories already exist		 
		"""

		if workdir==None: workdir="./%s" % (self.get_branchacronym()) 
		
		tools.dirs.mkdir(workdir)
		self.workdir=workdir
		
		# Now must create the sub-directories:
		for subfolder in ["obs","sim","ml","pred","out"]:
			tools.dirs.mkdir(self._get_path(subfolder))


	def meas_psf(self, measfct):
		"""
		Measures the 3 x 3 PSF stamps of each subfield, and writes the info to pkl.
		"""
		for subfield in self.subfields:
			
			# We don't bother reading the starcat, and just make one
			
			stars = []
			for i in range(3):
				for j in range(3):
					stars.append( [0.5 + self.stampsize()/2.0 + i*self.stampsize(), 0.5 + self.stampsize()/2.0 + j*self.stampsize()] )
			stars = np.array(stars)
			
			starcat = astropy.table.Table([stars[:,0], stars[:,1]], names=('psfx', 'psfy'))
			#print starcat
			
			# To measure the stars, we attach the image:
			starcat.meta["img"] = tools.imageinfo.ImageInfo(
				filepath=self.starimgfilepath(subfield),
				xname="psfx",
				yname="psfy",
				stampsize=self.stampsize(),
				workdir=self._get_path("obs", "star_%i_measworkdir" % subfield)
				)
			
			starcat = measfct(starcat, branch=self)
			
			#print starcat
			
			tools.io.writepickle(starcat, self._get_path("obs", "star_%i_meascat.pkl" % subfield))
			
			
		
	def meas_obs(self, measfct, skipdone=True, ncpu=1, **kwargs):
		"""
		Runs measfct on the GREAT3 data, demonstrating branch 73.
		
		:param measfct: some user-defined shape measurement function
		:param skipdone: set to False to make me overwrite previous measurements
		:param ncpu: Maximum number of processes that should be used. Default is 1.
			Set to 0 for maximum number of available CPUs.
		:type ncpu: int
		
		All further kwargs will be passed to the measfct.
		
		"""
		
		# Lists that we will pass to meas.run.general():
		incatfilepaths = []
		outcatfilepaths = []
			
		for subfield in self.subfields:
			
			
			incat = io.readgalcat(self, subfield)
			
			# We add PSF info to this field. PSFs are already measured, and we just take the first one:
			
			starcat = tools.io.readpickle(self._get_path("obs", "star_%i_meascat.pkl" % subfield))
			starcat.meta = {} # Dump the "img" entry
			matchedstarcat = starcat[np.zeros(len(incat), dtype=int)]
			assert len(incat) == len(matchedstarcat)
			for colname in incat.colnames:
				if colname in matchedstarcat.colnames:
					raise RuntimeError("colname %s appears twice" % colname)
			
			incat = astropy.table.hstack([incat, matchedstarcat], join_type="exact", metadata_conflicts="error")
			
			#print incat.colnames
			
			# Add the reference to the img and psf stamps:
			
			incat.meta["img"] = tools.imageinfo.ImageInfo(
				filepath=self.galimgfilepath(subfield),
				xname="x",
				yname="y",
				stampsize=self.stampsize(),
				workdir=self._get_path("obs", "img_%i_measworkdir" % subfield)
				)
		
			incat.meta["psf"] = tools.imageinfo.ImageInfo(
				filepath=self.starimgfilepath(subfield),
				xname="psfx",
				yname="psfy",
				stampsize=self.stampsize(),
				workdir=None
				)
		
			# Write the input catalog
			incatfilepath = self._get_path("obs", "img_%i_incat.pkl" % subfield)
			tools.io.writepickle(incat, incatfilepath)
			incatfilepaths.append(incatfilepath)
			
			# Prepare the filepath for the output catalog
			outcatfilepath = self._get_path("obs", "img_%i_meascat.pkl" % subfield)
			outcatfilepaths.append(outcatfilepath)

		# We pass some kwargs for the measfct
		measfctkwargs = {"branch":self}
		measfctkwargs.update(kwargs)

		# And we run all this
		meas.run.general(incatfilepaths, outcatfilepaths, measfct, measfctkwargs=measfctkwargs,
			ncpu=ncpu, skipdone=skipdone)

		
			
	def make_sim(self, simparams, n, ncat=1, nrea=1, ncpu=1):
		"""
		
		"""
		
		for subfield in self.subfields:
			
			simdir = self._get_path("sim","%03i" % subfield)
			
			starcat = tools.io.readpickle(self._get_path("obs", "star_%i_meascat.pkl" % subfield))
			drawcatkwargs = {"n":n, "stampsize":self.stampsize()}
			
			# We have to read in the obs catalog of this subfield to get the noise of the sky:
			obscat = tools.io.readpickle(self._get_path("obs", "img_%i_meascat.pkl" % subfield))
			sig = np.ma.mean(obscat["adamom_skymad"])
			simparams.sig = sig
			
			sim.run.multi(simdir, simparams, drawcatkwargs, psfcat=starcat, psfselect="random",
				ncat=ncat, nrea=nrea, ncpu=ncpu)
			


	   
	def meas_sim(self, simparams, measfct, groupcols=None, removecols=None, ncpu=1):
		"""		
		
		Stores all ouput in directories using simparams.name
		"""
		
		measfctkwargs = {"branch":self}
		
		for subfield in self.subfields:
			
			simdir = self._get_path("sim","%03i" % subfield)
			measdir = self._get_path("simmeas","%03i" % subfield)
		
			
			meas.run.onsims(simdir, simparams, measdir, measfct, measfctkwargs, ncpu=ncpu)
			
			avgcat = meas.avg.onsims(measdir, simparams, groupcols=groupcols, removecols=removecols, removereas=False)
			
			tools.io.writepickle(avgcat, self._get_path("simmeas", "%03i" % subfield, simparams.name, "avgcat.pkl"))
			
			
			# To make things easier for plots of single-realization stuff, we copy a single realization meascat
			
			simmeasdict = meas.utils.simmeasdict(measdir, simparams)
			firstmeascatdir = simmeasdict.items()[0][0]
			firstmeascatfilename = simmeasdict[firstmeascatdir][0]
			firstmeascatfilepath = self._get_path("simmeas", "%03i" % (subfield), simparams.name, firstmeascatfilename)
			shutil.copy(firstmeascatfilepath, self._get_path("simmeas", "%03i" % subfield, simparams.name, "rea0cat.pkl"))
			


	def train(self, trainparams, trainname, simname, ncpu=1):
		"""
		
		simname is the simparams.name of the simparams to be trained with
		
		Stores all output in directories usign both trainname and simname (simname == simparams.name)
		"""
		
		for subfield in self.subfields:
		
			simdir = self._get_path("sim", "%03i" % subfield)
			measdir = self._get_path("simmeas", "%03i" % subfield)
			
			# We load the right avg catalog (location depends on simname):
			avgcat = tools.io.readpickle(self._get_path("simmeas", "%03i" % subfield, simname, "avgcat.pkl"))
			
			# Reject crap measurements here
			ngroupstats = avgcat.meta["ngroupstats"]
			avgcat = avgcat[avgcat["adamom_flux_n"] > float(ngroupstats)/2.0] # At least half of the reas could be measured
			logger.info("Keeping %i galaxies for training" % (len(avgcat)))
			
			# We will store all the ouput here:
			traindir = self._get_path("ml", "%03i" % subfield, trainname, simname)
		 	if not os.path.exists(traindir):
				os.makedirs(traindir)
			
			# Before training, let's save the input catalog (e.g., for later self-predictions):
			tools.io.writepickle(avgcat, os.path.join(traindir, "traincat.pkl"))
					
			learn.run.train(avgcat, traindir, trainparams, ncpu=ncpu)
			

			

	def self_predict(self, trainparams, trainname, simname):
		"""
		
		
		"""
		
		for subfield in self.subfields:
		
			traindir = self._get_path("ml", "%03i" % subfield, trainname, simname)
			traincat = tools.io.readpickle(os.path.join(traindir, "traincat.pkl"))
			
			pretraincat_rea0 = learn.run.predict(traincat, traindir, trainparams, mode="first")
			tools.io.writepickle(pretraincat_rea0, os.path.join(traindir, "pretraincat_rea0.pkl"))
		
		
	
			
	def predict(self, trainparams, trainname, simname):
		"""

		"""

					
		for subfield in self.subfields:
		
			
			# We read the obs measurements
			obscat = tools.io.readpickle(self._get_path("obs", "img_%i_meascat.pkl" % subfield))
		
			traindir = self._get_path("ml", "%03i" % subfield, trainname, simname)
			
			preobscat = learn.run.predict(obscat, traindir, trainparams, mode="single")
			
			# And we save the predictions
			
			predir = self._get_path("pred", "%03i" % subfield, trainname, simname)
			
			if not os.path.exists(predir):
				os.makedirs(predir)
			
			tools.io.writepickle(preobscat, os.path.join(predir, "preobscat.pkl"))
		
				
	def writeout(self, trainname, simname):
		"""
	
		"""
		for subfield in self.subfields:
		
			preobscat = tools.io.readpickle(self._get_path("pred", "%03i" % subfield, trainname, simname, "preobscat.pkl"))
			
			# We replace masked predictions with 20.0
			preobscat["pre_g1"][preobscat["pre_g1"].mask] = 20.0
			preobscat["pre_g2"][preobscat["pre_g2"].mask] = 20.0
			
			# We cut out the columns we need
			preobscat = preobscat["ID","pre_g1","pre_g2"]
			
			# We write the ascii file
			preobscat.write(self._get_path("out", "%03i.cat" % subfield), format="ascii.commented_header")
			
			logger.info("Wrote shear cat for subfield %03i" % subfield)
			
			
	def presubmit(self, corr2path=".", presubdir=".", use_weights=False):
		"""
		:param corr2path: The directory containing the Michael Jarvis's corr2 code, 
				which can be downloaded from http://code.google.com/p/mjarvis/.
		:param use_weights: is the shear catalogue using weights?
		
	
		"""
		# Nope...
		#presubdir = os.path.join(os.path.dirname(__file__), "presubmission_script")
		
		presubscriptpath = os.path.join(presubdir, "presubmission.py")
		catpath = self._get_path("out", "*.cat")
		branchcode = self.branchcode()
		corr2path = os.path.join(corr2path, 'corr2')
		outfilepath=self._get_path("out", "%s.cat" % branchcode)

		if use_weights:
			cmd = "python %s %s -b %s -w 3 -c2 %s -o %s" % (presubscriptpath, catpath, 
																branchcode, corr2path, outfilepath)
		else:
			logger.info("I am NOT using weights !")
			cmd = "python %s %s -b %s -c2 %s -o %s" % (presubscriptpath, catpath, branchcode,
															corr2path, outfilepath)
				
		os.system(cmd)

	def _get_path(self,*args):
		"""
		A helper function that returns the filepath
		
		:param args: must be in order of the filepath, similar to os.path.join()
		
		Example usage::
		
			>>> self._get_path("obs","catalogue_000.fits")
			
		will return the filepath: self.workdir/obs/catalogue_000.fits
		"""
		return os.path.join(self.workdir,"/".join(args))
