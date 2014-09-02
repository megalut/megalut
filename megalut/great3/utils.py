"""
General utility stuff for GREAT3
"""

import os


class Branch:
	"""
	A class to define the file paths of the GREAT3 data and other branch-specific stuff.
	For now I commented-out all the MegaLUT output things. They are a priori not related to GREAT3.
	"""

	def __init__(self, experiment, obstype, sheartype, datadir=None, workdir=None):
	
		assert experiment in ['control', 'real_galaxy', 'variable_psf', 'multiepoch', 'full']
		assert obstype in ['ground', 'space']
		assert sheartype in ['constant', 'variable']
		
		self.experiment = experiment
		self.obstype = obstype
		self.sheartype = sheartype
	
		self.datadir = datadir
		"""Root directory of the unzipped GREAT3 data"""
		
		#self.workdir = workdir
		
	
	def branchtuple(self):
		"""
		The branch codes in form of a tuple
		"""
		return(self.experiment, self.obstype, self.sheartype)
	

	def __str__(self):
		return "Branch (%s, %s, %s)" % self.branchtuple()
	

	def stampsize(self):
		"""
		The stamp size "s" of this branch, in pixels
		"""
		if self.obstype == "ground":
			return 48
		elif self.obstype == "space":
			return 96

	
	def branchdir(self):
		"""
		Where all the data is
		"""
		return os.path.join(self.datadir, "/".join(self.branchtuple()))


	# For now we online define here the "input" stuff, set by GREAT3.
	# The MegaLUT output could be rethought, and is commented out.

	def galimgfilepath(self, subfield, epoch=0):
		return os.path.join(self.branchdir(), "image-%03i-%i.fits" % (subfield, epoch)) # This is set by GREAT3

	def psfimgfilepath(self, subfield, epoch=0):
		return os.path.join(self.branchdir(), "starfield_image-%03i-%i.fits" % (subfield, epoch)) # This is set by GREAT3

	def galcatfilepath(self, subfield):
		return os.path.join(self.branchdir(), "galaxy_catalog-%03i.txt" % (subfield)) # This is set by GREAT3
		
	def starcatpath(self, subfield):
		return os.path.join(self.branchdir(), 'star_catalog-%03i.txt' % subfield) # This is set by GREAT3




# 
# 	def obsstarsexpath(self, subfield):
# 		return os.path.join(self.obsdir(), 'star_catalog-%03i.txt' % subfield)
# 
# 	def obsgalfilepath(self, subfield):
# 		return os.path.join(self.obsdir(), "obs-%03i.pkl" % (subfield))
# 
# 	def obsstarfilepath(self, subfield):
# 		return os.path.join(self.obsdir(), "obs-star-%03i.pkl" % (subfield))
# 
# 	def precoaddpsfimgfilepath(self, subfield):
# 		return os.path.join(self.precoadddir(), "coadd_starfield_image-%03i.fits" % (subfield))
# 
# 	
# 	def obsdir(self): # Measurements on observations will go here
# 		if self.denoise:
# 			return os.path.join(self.workdir, "obs-" + "-".join(self.branch) + "-%s-den%s" % (self.version, self.denoise))
# 		else:
# 			return os.path.join(self.workdir, "obs-" + "-".join(self.branch) + "-%s" % (self.version))
# 	
# 	def simdir(self): # Simulation related stuff will go here
# 		if self.denoise:
# 			return os.path.join(self.workdir, "sim-" + "-".join(self.branch) + "-%s-den%s" % (self.version, self.denoise))
# 		else:
# 			return os.path.join(self.workdir, "sim-" + "-".join(self.branch) + "-%s" % (self.version))
# 	
# 	def outdir(self): # Submission files will go here
# 		if self.denoise:
# 			return os.path.join(self.workdir, "out-" + "-".join(self.branch) + "-%s-den%s" % (self.version, self.denoise))
# 		else:	
# 			return os.path.join(self.workdir, "out-" + "-".join(self.branch) + "-%s" % (self.version))
# 	
# 	
# 	def subfilepath(self): # the final submission file
# 		if self.denoise:
# 			return os.path.join(self.workdir, "out-" + "-".join(self.branch) + "-%s-den%s.txt" % (self.version, self.denoise))
# 		else:	
# 			return os.path.join(self.workdir, "out-" + "-".join(self.branch) + "-%s.txt" % (self.version))
# 	
# 	
# 
# 	def check_dir(self):
# 		# Making sure all the directories are there:
# 		if self.denoise:
# 			#Observation
# 			if not os.path.exists(self.denbranchdir()):
# 				os.makedirs(self.denbranchdir())
# 		# Observation
# 		if not os.path.isdir(self.obsdir()):
# 			os.mkdir(self.obsdir())
# 		# Simulations
# 		if not os.path.isdir(self.simdir()):
# 			os.mkdir(self.simdir())
# 		# Outdir
# 		if not os.path.exists(self.outdir()):
# 			os.mkdir(self.outdir())
# 
# 	def precoadddir(self):
# 		if len(self.precoadd) == 0:
# 			raise RuntimeError("Ouch, I don't know where is the precoadd data !")
# 		return os.path.join(self.workdir, "obs-" + "-".join(self.branch) + "-coadd-" + self.precoadd)
# 	
# 
# 		# Stuff related to the observations
# 		
# 
# 	def denobsgalimgfilepath(self, subfield, epoch=0):
# 		return os.path.join(self.denbranchdir(), "image-%03i-%i.fits" % (subfield, epoch))
# 	
# 	def precoaddgalimgfilepath(self, subfield):
# 		return os.path.join(self.precoadddir(), "coadd_image-%03i.fits" % (subfield))
# 
# 
# 		# Stuff related to the simulations
# 		
# 	def simgalimgfilepath(self, subfield, nimg=None):
# 		if nimg == None:
# 			return os.path.join(self.simdir(), "sim-%03i-galimg.fits" % (subfield))
# 		else:
# 			return os.path.join(self.simdir(), "sim-%03i-%02i-galimg.fits" % (subfield,nimg))
# 		
# 	def densimgalimgfilepath(self, subfield):
# 		return os.path.join(self.simdir(), "sim-%03i-galimg-den.fits" % (subfield))
# 	
# 	def simgalfilepath(self, subfield,nimg):
# 		if nimg == None:
# 			return os.path.join(self.simdir(), "sim-%03i.pkl" % (subfield))
# 		else:
# 			return os.path.join(self.simdir(), "sim-%03i-%02i.pkl" % (subfield,nimg))
# 
# #	def simstarfilepath(self, subfield):
# #		return os.path.join(self.obsdir(), "sim-star-%03i.pkl" % (subfield))
# 	
# 	def simtrugalimgfilepath(self, subfield,nimg):
# 		return os.path.join(self.simdir(), "sim-%03i-%02i-trugalimg.fits" % (subfield,nimg))
# 
# 	def simpsfimgfilepath(self, subfield,nimg):
# 		return os.path.join(self.simdir(), "sim-%03i-%02i-psfimg.fits" % (subfield,nimg))
# 	
# 	

