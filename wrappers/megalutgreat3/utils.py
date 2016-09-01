"""
General utility stuff for GREAT3
"""

import os

class Branch:
	"""
	A class to define the file paths of the GREAT3 data and other branch-specific stuff.
	This is to tell code where GREAT3 stuff is.
	It's NOT to tell code where to write (intermediary) files or to specify workdirs etc!
	So in fact there should be no MegaLUT related things in here.
	"""

	def __init__(self, experiment, obstype, sheartype, datadir=None):
	
		assert experiment in ['control', 'real_galaxy', 'variable_psf', 'multiepoch', 'full']
		assert obstype in ['ground', 'space']
		assert sheartype in ['constant', 'variable']
		
		self.experiment = experiment
		self.obstype = obstype
		self.sheartype = sheartype
	
		self.datadir = datadir
		"""Root directory of the unzipped GREAT3 data"""
		
	
	def branchtuple(self):
		"""
		The branch codes in form of a tuple
		"""
		return(self.experiment, self.obstype, self.sheartype)
	
	def branchcode(self):
		"""
		The branch codes in form of a tuple
		"""
		return "%s-%s-%s" % (self.experiment, self.obstype, self.sheartype)
	
	def get_branchacronym(self):
		"""
		Get the acrnonym of the branch (e.g. cgv)
		"""
		return "".join([self.experiment[0], self.obstype[0], self.sheartype[0]])
	

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
		
	def ntiles(self):
		if self.experiment in ['control', 'real_galaxy', 'multiepoch']:
			return 1
		if self.obstype == "ground":
			return 5
		elif self.obstype == "space":
			return 20
		
	def pixelscale(self):
		"""
		The pixel scale of this branch, in pixels
		"""
		if self.obstype == "ground":
			return 0.2
		elif self.obstype == "space":
			if self.experiment=="multiepoch":
				return 0.1
			else:
				return 0.05

	def gain(self):
		"""
		It seems that GREAT3 images are given in scaled electrons, but it doesn't matter as noise is just stationarry Gaussian anyway.
		For SExtractor one should set gain = 0 which corresponds to infinity to get this Gaussian noise right.
		"""
		return 1.0

	
	def branchdir(self):
		"""
		Where all the data is
		"""
		return os.path.join(self.datadir, "/".join(self.branchtuple()))


	# For now we only define here the "input" stuff, set by GREAT3.
	# The MegaLUT output could be rethought, and is commented out.
	
	def get_ftiles(self, xt, yt):
		"""
		A little helper for the name of the files generator functions below. It handles the tile id
		"""
		if not (xt is None or yt is None):
			return "-%02d-%02d" % (xt,yt)
		else:
			return ""


	def galimgfilepath(self, subfield, xt=None, yt=None,epoch=0, folder=None):
		if folder==None:
			folder=self.branchdir()
		return os.path.join(folder, "image-%03i-%i%s.fits" % (subfield, epoch, self.get_ftiles(xt,yt))) # This is set by GREAT3


	def starimgfilepath(self, subfield, xt=None, yt=None, epoch=0):
		return os.path.join(self.branchdir(), "starfield_image-%03i-%i%s.fits" % 
						(subfield, epoch, self.get_ftiles(xt,yt))) # This is set by GREAT3


	def galcatfilepath(self, subfield, xt=None, yt=None, folder=None):
		if folder==None:
			folder=self.branchdir()

		fname="galaxy_catalog-%03i%s.txt" % (subfield,self.get_ftiles(xt,yt))
		return os.path.join(folder, fname) # This is set by GREAT3

		
	def starcatfilepath(self, subfield, xt=None, yt=None, folder=None):
		if folder==None:
			folder=self.branchdir()
		return os.path.join(folder, 'star_catalog-%03i%s.txt' % \
						(subfield,self.get_ftiles(xt,yt))) # This is set by GREAT3
	
	
	
	
