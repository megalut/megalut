"""
Top-level classes and functions to help running MegaLUT on GREAT3.
"""

import logging
logger = logging.getLogger(__name__)

from astropy.table import Table
import os

import utils
from megalut import tools



class GREAT3Run(utils.Branch):
	"""
	This is a simple class to group frequently used variables, on top of the Branch class.
	Unlike Branch, it does specify paths to MegaLUT-internal temporary files and directories, and handles a workdir.
	"""
	
	def __init__(self, experiment, obstype, sheartype, datadir, truthdir, workdir, g3publicdir, subfields=None, ncpu=None, skipdone=False):
		
		utils.Branch.__init__(self, experiment, obstype, sheartype, datadir, truthdir)
		logger.info("Getting ready to work on branch %s-%s-%s" % (experiment, obstype, sheartype))

		self.workdir=workdir
		if self.workdir == None:
			logger.warning("Better specify a workdir, I think.")
			self.workdir = "./%s" % (self.get_branchacronym())
		self.mkdirs()
		
		self.g3publicdir = g3publicdir
		
		self.subfields=subfields
		if self.subfields is None:
			self.subfields=range(200)
			
		self.ncpu = ncpu
		if ncpu is None:
			self.ncpu = 1
			
		self.skipdone = skipdone

		# Those, and further variables, can be wildly added later:
		self.simparams_name = None
		self.trainparams_name = None
		

	
	def __str__(self):
		"""
		A tiny self-description, for logging
		"""
		return "GREAT3Run on branch %s in workdir '%s'" % (self.get_branchacronym(), self.workdir)

		
	def mkdirs(self, subfield=None):
		"""
		Creates the working directories. 
		"""

		if not os.path.isdir(self.workdir):
			os.makedirs(self.workdir)
	
		if subfield is not None:
			dirpath = self.subpath(subfield)
			if not os.path.isdir(dirpath):
				os.makedirs(dirpath)
				
			# Now must create the sub-directories:
			for subfolder in ["obs","sim","ml","pred","out","val"]:
				dirpath = self.subpath(subfield, subfolder)
				if not os.path.isdir(dirpath):
					os.makedirs(dirpath)


	def path(self,*args):
		"""
		A helper function that returns a filepath within the working directory.
		
		:param args: strings, must be in order of the filepath, similar to os.path.join()
		
		Example usage::
		
			>>> self.path("obs","catalogue_000.fits")
			
		will return the filepath: self.workdir/obs/catalogue_000.fits
		"""
		return os.path.join(self.workdir,"/".join(args))
	
	
	def subpath(self, subfield, *args):
		"""
		Similar, but first argument is a subfield number
		"""
		
		
		
		return os.path.join(self.workdir, "%03i" % subfield, "/".join(args))
	

	# Files that MegaLUT will write: 
	
#	def obsincat(self, subfield, imgtype, prefix="", xt=None, yt=None):
#		"""
#		Please document
#		Should use get_path
#		what is imgtype for ?
#		"""
#	
#		return os.path.join(self.workdir, imgtype, "%simage-%03i-0%s_meascat.pkl" % \
#						(prefix,subfield,self.get_ftiles(xt,yt)))
#	
#	def galinfilepath(self, subfield, imgtype, xt=None, yt=None, prefix=""): 
#		"""
#		Please document
#		"""
#		return os.path.join(self.workdir, imgtype, "%sinput_image-%03i-0%s_meascat.pkl" % \
#						(prefix,subfield,self.get_ftiles(xt,yt)))
#	
#	
#	# Stuff related to the simulations
#		
#	def simgalcatfilepath(self, subfield, nimg=None):
#		"""
#		Please document
#		"""
#		if nimg == None:
#			return self.galcatfilepath(subfield, folder=os.path.join(self.workdir,"sim"))
#		else:
#			raise NotImplemented()
#		
#	def simgalimgfilepath(self, subfield, xt=None, yt=None, nimg=None):
#		"""
#		Please document
#		"""
#		if not (xt is None or yt is None):
#			note="/%02dx%02d" % (xt,yt)
#		else:
#			note=""
#		
#		if nimg == None:
#			return self.galimgfilepath(subfield, folder=os.path.join(self.workdir,"sim%s" % note))
#		else:
#			raise NotImplemented()
#
#
#
#
#	def presubmit(self, corr2path=".", presubdir=".", use_weights=False):
#		"""
#		:param corr2path: The directory containing the Michael Jarvis's corr2 code, 
#				which can be downloaded from http://code.google.com/p/mjarvis/.
#		:param use_weights: is the shear catalogue using weights?
#		
#	
#		"""
#		# Nope...
#		#presubdir = os.path.join(os.path.dirname(__file__), "presubmission_script")
#		
#		presubscriptpath = os.path.join(presubdir, "presubmission.py")
#		catpath = self.path("out", "*.cat")
#		branchcode = self.branchcode()
#		corr2path = os.path.join(corr2path, 'corr2')
#		outfilepath=self.path("out", "%s.out" % branchcode)
#
#		if use_weights:
#			cmd = "python %s %s -b %s -w 3 -c2 %s -o %s" % (presubscriptpath, catpath, 
#																branchcode, corr2path, outfilepath)
#		else:
#			logger.info("I am NOT using weights !")
#			cmd = "python %s %s -b %s -c2 %s -o %s" % (presubscriptpath, catpath, branchcode,
#															corr2path, outfilepath)
#				
#		os.system(cmd)
#	
#
#	def save_run(self, outdir=None, fname='great3_config.pkl'):
#		"""
#		Saves the current Object to a specified `outdir` or directly into `self.workdir`
#		"""
#		
#		if outdir is None:
#			outdir = self.workdir
#			
#		tools.io.writepickle(self, os.path.join(self.workdir, fname))
#		
#
#
#	
#def load_run(outdir, fname='great3_config.pkl'):
#	
#	return tools.io.readpickle(os.path.join(outdir, fname))
#
#
#
#def load_true_shape(truthdir, experiment, obstype, sheartype, subfield, epoch=0):
#	
#	fname = os.path.join(truthdir, experiment, obstype, sheartype, "epoch_catalog-{:03d}-{:d}.fits".format(subfield, epoch))
#		
#	return Table.read(fname)

