"""
Quick and dirty GREAT3 Run class making use of the new code of branch #73
"""

import logging
logger = logging.getLogger(__name__)

import os

import utils
from megalut import tools


class Great3(utils.Branch):
	"""
	This is a simple class to handle variables
	"""
	
	def __init__(self, experiment, obstype, sheartype, datadir=None, workdir=None,\
				  subfields=range(200)):
		
		utils.Branch.__init__(self, experiment, obstype, sheartype, datadir, workdir)
		logger.info("Working on branch %s-%s-%s" % (experiment, obstype, sheartype))

		self._mkdir(workdir)
		self.subfields=subfields
		self.simparams_name = None
		self.trainparams_name = None
		
	def _mkdir(self, workdir):
		"""
		Creates the working directories. Outputs a warning if the directories already exist		 
		"""

		if workdir==None: workdir="./%s" % (self.get_branchacronym()) 
		
		tools.dirs.mkdir(workdir)
		self.workdir=workdir
		
		# Now must create the sub-directories:
		for subfolder in ["obs","sim","ml","pred","out"]:
			tools.dirs.mkdir(self.get_path(subfolder))

	def get_path(self,*args):
		"""
		A helper function that returns the filepath
		
		:param args: must be in order of the filepath, similar to os.path.join()
		
		Example usage::
		
			>>> self._get_path("obs","catalogue_000.fits")
			
		will return the filepath: self.workdir/obs/catalogue_000.fits
		"""
		return os.path.join(self.workdir,"/".join(args))
	
	def presubmit(self, corr2path=".", presubdir=".", use_weights=False):
		"""
		:param corr2path: The directory containing the Michael Jarvis's corr2 code, 
				which can be downloaded from http://code.google.com/p/mjarvis/.
		:param use_weights: is the shear catalogue using weights?
		
	
		"""
		# Nope...
		#presubdir = os.path.join(os.path.dirname(__file__), "presubmission_script")
		
		presubscriptpath = os.path.join(presubdir, "presubmission.py")
		catpath = self.get_path("out", "*.cat")
		branchcode = self.branchcode()
		corr2path = os.path.join(corr2path, 'corr2')
		outfilepath=self.get_path("out", "%s.cat" % branchcode)

		if use_weights:
			cmd = "python %s %s -b %s -w 3 -c2 %s -o %s" % (presubscriptpath, catpath, 
																branchcode, corr2path, outfilepath)
		else:
			logger.info("I am NOT using weights !")
			cmd = "python %s %s -b %s -c2 %s -o %s" % (presubscriptpath, catpath, branchcode,
															corr2path, outfilepath)
				
		os.system(cmd)
	
	def save_config(self, outdir=None, fname='great3_config.pkl'):
		"""
		Saves the current configuration to a specified `outdir` or directly into `self.workdir`
		"""
		
		if outdir is None:
			outdir = self.workdir
			
		tools.io.writepickle(self, os.path.join(self.workdir, fname))
		
def load_config(outdir, fname='great3_config.pkl'):
	
	return tools.io.readpickle(os.path.join(outdir, fname))
