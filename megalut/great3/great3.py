"""
Helper class for GREAT3 that does the trivial tasks for the user.

Todo list
---------
* make this inherit a generic run class

"""
import logging
logger = logging.getLogger(__name__)

import os
#from astropy.table import Table
import astropy

import numpy as np

import utils
import io
from .. import sim
from .. import tools
from .. import learn
from .. import meas

import copy
import glob
import shutil

class Run(utils.Branch):
	
	def __init__(self, experiment, obstype, sheartype, datadir=None, workdir=None,\
				  subfields=range(200)):
		
		utils.Branch.__init__(self,experiment, obstype, sheartype, datadir, workdir)

		self._mkdir(workdir)
		self.subfields=subfields
		
		if self.sheartype == "constant":
			self.simsubfields = subfields
		elif self.sheartype == "variable":
			self.simsubfields = np.asarray(subfields)/20.
			self.simsubfields=self.simsubfields.astype(np.int)
			self.simsubfields *= 20
			self.simsubfields = np.unique(self.simsubfields)

		logger.info("Starting new GREAT3 branch %s-%s-%s" % (experiment, obstype, sheartype))
		
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
			
	   
	   
	def meas_sim(self, imgtype, measfct, measfctkwargs, simparams="",
		groupcols=None, removecols=None, overwrite=False, ncpu=1):
		"""
		Made a new func for this, given the completely different signature.
		Still has to be finalized.
		
		:param groupcols: Passed to :func:`megalut.meas.avg.onsims`, 
			if groupcols=None default = adamom features
		:param removecols: Passed to :func:`megalut.meas.avg.onsims`
		
		"""


		for simsubfield in self.simsubfields:
			img_fname=self.simgalimgfilepath(simsubfield)
			simdir=self._get_path(imgtype,"%03d" % simsubfield)
		
			meas.run.onsims(simdir, simparams, simdir, measfct, measfctkwargs, ncpu, skipdone)
			
			if groupcols==None:
				groupcols = [
				"adamom_flux", "adamom_x", "adamom_y", "adamom_g1", "adamom_g2",
				"adamom_sigma", "adamom_rho4",
				"adamom_skystd", "adamom_skymad", "adamom_skymean", "adamom_skymed", "adamom_flag"
				]
			if removecols==None:
				removecols=[]
			
			avgcat = meas.avg.onsims(simdir, simparams,
							groupcols=groupcols,removecols=removecols,removereas=True)
			for simd in meas.utils.simmeasdict(simdir, simparams):
				fname = '%s_avg_galimg_meascat.pkl' % simd
				tools.dirs.mkdir(os.path.join(simdir,"meas",simparams.name))
				fname=os.path.join(simdir,"meas",simparams.name,fname)
				tools.io.writepickle(avgcat,fname)
		
			
	def sim(self, simparams, n, overwrite=False, psf_selection=[4],ncat=1,nrea=1,ncpu=1):
		"""
		Does the simulation
		
		:param simparams: an (overloaded if needed) megalut.sim.params.Params instance
		:param n: square root of the number of simulation
		:param overwrite: *deprecated* if `True` and the simulation exist they are deleted and simulated.
		:param psf_selection: Which PSF(s) to use in the catalogue ? Chosen from a random pick
			into a eligible PSF catalogue. Default: the center (ie 4th) PSF.
		:param ncat: The number of catalogs to be generated.
		:type ncat: int
		:param nrea: The number of realizations per catalog to be generated.
		:type nrea: int
		:param ncpu: Maximum number of processes that should be used. Default is 1.
			Set to 0 for maximum number of available CPUs.
		:type ncpu: int
		
		.. note: for an example of simparams have a look at demo/gret3/demo_CGV.py
		"""
		
		for simsubfield in self.simsubfields:
			# TODO: the +5 is only to make the code work in the presence of images 5--9
			matched_psfcat=Table.read(self.starcatpath(simsubfield+5), format="ascii")
			
			cat_fname=self._get_path("sim","galaxy_catalog-%03i.fits" % simsubfield)
			img_fname=self.simgalimgfilepath(simsubfield)
			
			simdir=self._get_path("sim","%03d" % simsubfield)
			
			# figure out if we need to overwrite (if applicable)
			if os.path.exists(cat_fname) and os.path.exists(img_fname):
				if overwrite: 
					logger.info("Sim of subfield %d, I'm told to overwrite..." % (simsubfield))
					os.remove(cat_fname)
				else: 
					logger.info("Sim of subfield %d already exists, skipping..." % (simsubfield))
					continue
			elif os.path.exists(cat_fname):
				os.remove(cat_fname)
				logger.warning("catalog (subfield %d) only was found, removing it" % (simsubfield))
			elif os.path.exists(img_fname):
				os.remove(img_fname)
				logger.warning("image (subfield %d) only was found, removing it" % (simsubfield))
				
			psf_selected=np.random.choice(psf_selection,n*n)
			matched_psfcat = matched_psfcat[psf_selected]
			matched_psfcat.meta["stampsize"]=self.stampsize()
			
			psfimg=tools.image.loadimg(self.psfimgfilepath(simsubfield+5))
				
			drawcatkwargs = {"n":n, "stampsize":self.stampsize()}
			drawimgkwargs = {"psfcat":matched_psfcat,'psfimg':psfimg,
							 "psfxname":"col1", "psfyname":"col2"}
			matched_psfcat["col1"]+=1
			matched_psfcat["col2"]+=1
			sim.run.multi(simdir, simparams,
						  drawcatkwargs, drawimgkwargs, ncat, nrea, ncpu)

	def learn(self, learnparams, mlparams, simparam_name, suffix="_mean", 
			  method_prefix="", overwrite=False):
		"""
		A method that train any given algorithm.
		
		:param learnparams: an instance of megalut.learn.MLParams
		:param mlparams: an instance of :class:`megalut.learn.fannwrapper.FANNParams`
		:param suffix: what suffix of the measurements to take ? Default: "_mean". 
		:param method_prefix: *deprecated* the prefix of the features
		:param simparam_name: the name of the simulation to use
		:param overwrite: if `True` and the output ML file exist they are deleted and re-trained.
		
		
		Example usage::
		
			>>> learnparams = megalut.learn.MLParams(
					name = "demo",
					features = ["gs_g1", "gs_g2", "gs_flux"],
					labels = ["tru_g1","tru_g2"],
					predlabels = ["pre_g1","pre_g2"],
					)
			
			>>> fannparams=megalut.learn.fannwrapper.FANNParams(
					hidden_nodes = [20, 20],
					max_iterations = 500,
				)
				
			>>> great3.learn(learnparams=learnparams, mlparams=fannparams)
		"""
		# TODO: how to merge different measurements together ?
		
		for simsubfield in self.simsubfields:	   
			
			# a deepcopy is made to make sure we don't use modified catalogs 
			# (see right after ml.train())
			lp=copy.deepcopy(learnparams)
			lp.features = [feature + suffix for feature in lp.features]

			ml = learn.ML(lp, mlparams,workbasedir=os.path.join(self.workdir,
																		 "ml","%03d" % simsubfield))
						
			ml_dir=ml.get_workdir()
			exists=True
			if not os.path.exists(os.path.join(ml_dir,"ML.pkl")) :
				exists=False

			if exists and not overwrite:
				logger.info("Learn of simsubfield %d already exists, skipping..." % (simsubfield))
				continue
			elif overwrite and exists:
				logger.info("Learn of simsubfield %d, I'm told to overwrite..." % (simsubfield))
				shutil.rmtree(ml_dir)

			# This is a quick fix, only working with one catalog!
			seapat=self._get_path("sim","%03d" % simsubfield, "meas",
								  "%s" % simparam_name,"*_meascat.pkl")
			cats = glob.glob(seapat)
			if len(cats)==0:
				raise ValueError("No catalog found for subfield %d" % simsubfield)
			elif len(cats)>1:
				raise NotImplemented("I'm not foreseen to be that smart, calm down")
			
			input_cat = tools.io.readpickle(cats[0])
			# Important: we don't want to train on badly measured data!
			# If we take a suffix, this means we took out the badly measured data already
			#TODO: This line is bad, because method_prefix will disappear!
			if suffix=="":
				input_cat = input_cat[input_cat[method_prefix+"flag"] == 0] 

			ml.train(input_cat)
			
			# Removes the suffix from the ml params as we observe only once, and thus no average
			for i, f in enumerate(ml.mlparams.features):
				if not suffix in f: continue
				ml.mlparams.features[i] = f[:-1*len(suffix)]
			
			# export the ML object:
			tools.io.writepickle(ml, os.path.join(ml_dir,"ML.pkl"))
			
	def predict(self,method_prefix="adamom_",overwrite=False):
		"""
		Predicts values according to the configuration of the ML pickles. 
		Predicts on all ML available.
		
		:param method_prefix: *deprecated* the prefix of the features
		:param overwrite: if `True` and the predictions exist they are deleted and re-predicted.
		"""

					
		for subfield in self.subfields:	  
			if self.sheartype == "constant":
				simsubfield = subfield
			elif self.sheartype == "variable":
				simsubfield = int(subfield/20)*20
			fpath =	 os.path.join(self.workdir,"ml","%03d" % simsubfield)
			for root, dirs, files in os.walk(fpath):
				if not "ML.pkl" in files: 
					logger.info("Nothing found in %s" % fpath)
					continue
				ml_name = root.split("/")[-1]
				
				cat_fname=self._get_path("pred","%s-%03d.fits" % (ml_name,subfield))
				if os.path.exists(cat_fname) and overwrite:
					logger.info("Pred of subfield %d, I'm told to overwrite..." % (subfield))
					os.remove(cat_fname)
				elif os.path.exists(cat_fname):
					logger.info("Pred of subfield %d already exists, skipping..." % (subfield))
					continue
				
				logger.info("Using %s to predict on subfield %03d" % (ml_name,simsubfield))

				ml=tools.io.readpickle(os.path.join(root,"ML.pkl"))
				
				input_cat=self.galfilepath(subfield,"obs")
				input_cat=tools.io.readpickle(input_cat)
				
				# We predict everything, we will remove flags later
				predicted=ml.predict(input_cat)
				#TODO: This line is bad, because method_prefix will disappear!
				failed=predicted[method_prefix+"flag"]>0
				count_failed=0
				for p in predicted[failed]:
					# TODO: Better and faster way to do this ?
					p["pre_g1"]=20.
					p["pre_g2"]=20.
					count_failed+=1
					
				logger.info("Predicted on %d objects, %d failed" % (len(input_cat),count_failed))
				
				predicted.write(cat_fname,format="fits")
				
	def writeout(self, ml_name):
		"""
		Write the shear catalog out
		
		:param ml_name: the name of the ML to use (from train & predict)
		"""
		for subfield in self.subfields:	 
			input_cat = Table.read(self._get_path("pred","%s-%03d.fits" % (ml_name,subfield)))
			
			input_cat=input_cat["ID","pre_g1","pre_g2"]
			input_cat.write(self._get_path("out","%03d.cat" % subfield),
							format="ascii.commented_header")
			logger.info("Wrote shear cat for subfield %03d" % subfield)
			
	def presubmit(self, corr2path=".", use_weights=False):
		"""
		:param corr2path: The directory containing the Michael Jarvis's corr2 code, 
				which can be downloaded from http://code.google.com/p/mjarvis/.
		:param use_weights: is the shear catalogue using weights?
		
		:requires: presubmission files in the megalut/great3/presubmission_script directory.
				Those files can be downloaded from https://github.com/barnabytprowe/great3-public.
		"""
		presubdir = os.path.join(os.path.dirname(__file__), "presubmission_script")
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
