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

	def __init__(self, experiment, obstype, sheartype, datadir=".", truthdir="."):
	
		assert experiment in ['control', 'real_galaxy', 'variable_psf', 'multiepoch', 'full']
		assert obstype in ['ground', 'space']
		assert sheartype in ['constant', 'variable']
		
		self.experiment = experiment
		self.obstype = obstype
		self.sheartype = sheartype
	
		self.datadir = datadir
		self.truthdir = truthdir 
		
		
	
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

	
	def branchdir(self, truth=False):
		"""
		Where all the data is
		If truth is True, returns the path within the truthdir instead.
		"""
		if truth is False:
			return os.path.join(self.datadir, "/".join(self.branchtuple()))
		else:
			return os.path.join(self.truthdir, "/".join(self.branchtuple()))


	# Now we only define here the paths to the "input" stuff, set by GREAT3.
	# No MegaLUT-internal files!
	
	
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
	
	
	def trushearfilepath(self, subfield, folder=None):
		if folder is None:
			folder = self.branchdir(truth=True)
		return os.path.join(folder, 'shear_params-%03i.txt' % (subfield))
	
	def trustarfilepath(self, subfield, folder=None):
		"""
		The psf g1 g2, used to "rotate" metrics
		"""
		if folder is None:
			folder = self.branchdir(truth=True)
		return os.path.join(folder, 'starshape_parameters-%03i-0.txt' % (subfield))
	


import megalut.tools.calc
import numpy as np

def metrics(cat, trucols, predcols, psfgcols, latex=True):
	"""
	Computes GREAT3 metrics m and c for 1, 2, + and x, including errors.
	trucols and predcols are tuples with column names, e.g. ("tru_s1", "tru_s2")
	
	It has been checked that results are identical to what the public great3 code gives (on the "simple" branches only).
	"""
	
	returndict = {}
	
	assert cat[trucols[0]].ndim == 1
	assert cat[predcols[1]].ndim == 1

	
	pixres1 = megalut.tools.calc.linreg(cat[trucols[0]], cat[predcols[0]], prob=0.68) # Component 1
	pixres2 = megalut.tools.calc.linreg(cat[trucols[1]], cat[predcols[1]], prob=0.68) # Component 2
	
	returndict["m1"] = pixres1["m"]
	returndict["m1err"] = pixres1["merr"]
	returndict["c1"] = pixres1["c"]
	returndict["c1err"] = pixres1["cerr"]
	
	returndict["m2"] = pixres2["m"]
	returndict["m2err"] = pixres2["merr"]
	returndict["c2"] = pixres2["c"]
	returndict["c2err"] = pixres2["cerr"]
	
	
	# Now the rotated metrics
	# This simply follows great3-public/metrics/evaluate
		
	# angles:
	rotations = .5 * np.arctan2(cat[psfgcols[1]], cat[psfgcols[0]]) # Note the inverted order of components
		
	# rotating predictions:
	g1prot = cat[predcols[0]] * np.cos(-2. * rotations) - cat[predcols[1]] * np.sin(-2. * rotations)
	g2prot = cat[predcols[0]] * np.sin(-2. * rotations) + cat[predcols[1]] * np.cos(-2. * rotations)
	
	# rotating truth:
	g1trot = cat[trucols[0]] * np.cos(-2. * rotations) - cat[trucols[1]] * np.sin(-2. * rotations)
	g2trot = cat[trucols[0]] * np.sin(-2. * rotations) + cat[trucols[1]] * np.cos(-2. * rotations)
 	
	
	pixresplus = megalut.tools.calc.linreg(g1trot, g1prot, prob=0.68)
	pixrescros = megalut.tools.calc.linreg(g2trot, g2prot, prob=0.68)
	
	returndict["m+"] = pixresplus["m"]
	returndict["m+err"] = pixresplus["merr"]
	returndict["c+"] = pixresplus["c"]
	returndict["c+err"] = pixresplus["cerr"]

	returndict["mx"] = pixrescros["m"]
	returndict["mxerr"] = pixrescros["merr"]
	returndict["cx"] = pixrescros["c"]
	returndict["cxerr"] = pixrescros["cerr"]



	if latex is True:
		
		kilo = {}
		for (key, value) in returndict.iteritems():
			kilo[key] = 1000.0 * value
		
		ret = ["Branch & ",
			"${r[m1]:+.2f}\pm{r[m1err]:.2f}$ & ".format(r=kilo),
			"${r[m2]:+.2f}\pm{r[m2err]:.2f}$ & ".format(r=kilo),
			"${r[m+]:+.2f}\pm{r[m+err]:.2f}$ & ".format(r=kilo),
			"${r[mx]:+.2f}\pm{r[mxerr]:.2f}$ & ".format(r=kilo),
			"${r[c1]:+.2f}\pm{r[c1err]:.2f}$ & ".format(r=kilo),
			"${r[c2]:+.2f}\pm{r[c2err]:.2f}$ & ".format(r=kilo),
			"${r[c+]:+.2f}\pm{r[c+err]:.2f}$ & ".format(r=kilo),
			"${r[cx]:+.2f}\pm{r[cxerr]:.2f}$ \\".format(r=kilo),
			]
			
		print "LaTeX table line:"
		print "".join(ret)
	
	return returndict
	
	
	
	
	
	

