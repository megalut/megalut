import numpy as np
import os
import megalut.tools as tl

import logging
logger = logging.getLogger(__name__)

def complex2geometrical(e1, e2, size=1., fact=1.):
	"""
	Convert e1, e2 to a, b, theta
	"""
	e = np.sqrt(e1**2 + e2**2)
	if fact != 1:
		e = np.clip(e * fact, -0.9, 0.9)
	a = np.sqrt(1. + e) * size
	b = np.sqrt(1. - e ) * size
	theta = np.arctan2(e2, e1) / 2.
	return a, b, theta

def geometrical2complex(a, b, theta):
	"""
	Convert a,b,theta to e1, e2
	"""
	chi = (a**2 - b**2) / (a**2 + b**2) * np.exp(2.j * theta)
	e1 = chi.real
	e2 = chi.imag
	return e1, e2

class PSF_Field():
	
	def __init__(self, kind, cx=0.5, cy=0.5, e_max=0.015, fwhm_max=0.14, fieldfname=None):
		"""
		:param kind: a string either "radial", "tangential", "e1", "e2", "fwhm", "e1e2", "euclid-like". They represent how the ellipticity varies.
		:param e_max: the maximum value of the ellipiticty
		:param fwhm_max: idem, FWHM in arcsec
		:param cx: x coordinate of center of frame
		:param cy: y coordinate of center of frame
		:param fieldfname: if loading from a pre-determined field, the path to the field pkl (for Euclid-like fields only)
		"""
		self.kind = kind
		self.e_max = e_max
		self.fwhm_max = fwhm_max
		self.cx = cx
		self.cy = cy
		self.fieldfname = fieldfname
		
		
		self.e = np.random.uniform(low=self.e_max*0.8, high=self.e_max)
		self.fwhm = np.random.uniform(low=self.fwhm_max*0.9, high=self.fwhm_max)
		self.dR = np.hypot(self.cx, self.cy)
		if self.kind == "fwhm":
			self.position_angle = np.random.uniform(0, np.pi)
		elif self.kind == "euclid-like":
			self._load_psf_field()
		elif self.kind == "e1e2":
			self.a = np.random.uniform(-.01, .01)
			self.b = np.random.uniform(-.01, .01)
			self.c = np.random.uniform(-.01, .01)
			
		logger.info('Created PSF field class, kind is {:s}, ellipt. is {:0.3f} and fwhm is {:0.3f}"'.format(kind, self.e, self.fwhm))

	def _load_psf_field(self):
		"""
		Happy helper to load the Euclid-like files
		"""
		self.psf_g1_interp, self.psf_g2_interp, self.psf_fwhm_interp = tl.io.readpickle(self.fieldfname)
		logger.info("Loaded Euclid-like psf field {}".format(self.fieldfname))

	def eval(self, x, y):
		"""
		Initialises the PSF field. The following option exists:
		
		* `radial`: construct a PSF that radiates from the center, the FWHM is smaller at the center and is 125% of that value at the edges
		* `tangential`: to simulate a PSF that is tangent to the center. FWHM is same as radial
		* `e1`: only e1 changes as a function of x, from -1 to 1. e2 and FWHM constant
		* `e2`: only e2 changes as a function of y, from -1 to 1. e1 and FWHM constant
		* `e1e2`: radial in e1 e2 plane.
		* `fwhm`: only FWHM changes as a function of x, from -1 to 1. Constant ellipticity
		* `euclid-like`: loads a Euclid-like PSF field generated from realistic parameters
		
		Note that the ellipticity, the base of the FWHM and the position angles (only for `fwhm`) can be changed after that this method has
		been called. 
		"""

		if self.kind == "radial":
			dx = x - self.cx 
			dy = y - self.cy
			dr = np.hypot(dx, dy)
			
			theta = np.arctan2(dy, dx)
			
			a = np.ones_like(x) * np.sqrt(1. + self.e)
			b = np.ones_like(x) * np.sqrt(1. - self.e)
			
			e1, e2 = geometrical2complex(a, b, theta)
			r = self.fwhm * (1.+dr/self.dR * 0.25) / 1.25
		elif self.kind == "tangential":
			dx = x - self.cx 
			dy = y - self.cy
			dr = np.hypot(dx, dy)
			
			theta = np.arctan2(dy, dx) + np.pi / 2.
			
			a = np.ones_like(x) * np.sqrt(1. + self.e)
			b = np.ones_like(x) * np.sqrt(1. - self.e)
			
			e1, e2 = geometrical2complex(a, b, theta)
			r = self.fwhm * (1.+dr/self.dR * 0.25) / 1.25
		elif self.kind == "e1":
			dx = x - self.cx 

			e1 = np.ones_like(x) * self.e * dx / (self.cx)
			e2 = np.zeros_like(x)
			r = np.ones_like(x) * self.fwhm
		elif self.kind == "e2":
			dy = y - self.cy

			e1 = np.zeros_like(x)
			e2 = np.ones_like(x) * self.e * dy / (self.cy)
			r = np.ones_like(x) * self.fwhm
				
		elif self.kind == "fwhm":
			dx = x - self.cx
			dy = y - self.cy
			dr = np.hypot(dx, dy)
			
			a = np.ones_like(x) * np.sqrt(1. + self.e)
			b = np.ones_like(x) * np.sqrt(1. - self.e)
			
			e1, e2 = geometrical2complex(a, b, self.position_angle)
			
			r = self.fwhm * (1.+dr/self.dR * 0.5) / 1.5
		elif self.kind == "e1e2":
			dx = x - self.cx 
			dy = y - self.cy
			dr = np.hypot(dx, dy)

			e1 = np.ones_like(x) * self.e * dx / (self.cx)
			e2 = np.ones_like(x) * self.e * dy / (self.cy)
			
			r = self.a * dx + self.b * dy + self.c * self.fwhm + self.fwhm
						
		elif self.kind == "euclid-like":
			e1 = self.psf_g1_interp.ev(x, y)
			e2 = self.psf_g2_interp.ev(x, y)
			r = self.psf_fwhm_interp.ev(x, y)
				
		else:
			raise NotImplemented()
		
		return e1, e2, r
	
	def save(self, outdir):
		if not os.path.exists(outdir):
			os.makedirs(outdir)
		tl.io.writepickle(self, os.path.join(outdir, "psf_field.pkl"))

	def plot(self, outdir=None):
		import matplotlib.pyplot as plt
		from matplotlib.patches import Ellipse
	
		# We'll generate a grid on which to visualise our PSF parameters.
		x = np.linspace(0, 1, 21)
		y = np.linspace(0, 1, 21)
		X, Y = np.meshgrid(x, y)
		XY = np.hstack((X.ravel()[:, np.newaxis], Y.ravel()[:, np.newaxis]))
		
		# Getting the PSF params at the requested positions...
		e1, e2, r = self.eval(XY[:,0], XY[:,1])
		# Plotting the e1, e2 space as a quiver plot
		fig = plt.figure(figsize=(22,6))
		ax = plt.subplot(131)
		plt.quiver(XY[:,0], XY[:,1], e1, e2)
		plt.xlabel("X image")
		plt.ylabel("Y image")
		plt.title("e1 - e2 space")
		plt.xlim(-0.05,1.05)
		plt.ylim(-0.05,1.05)
		
		# Now changing to the geometrical description of the PSF (and doing some rescaling)
		a, b, theta = complex2geometrical(e1, e2, r * 0.5, fact=20)
	
		# We can plot what the PSF will look like in the pixel space
		ax = plt.subplot(132, aspect='equal')
		
		for (x, y), a_, b_, t_ in zip(XY, a * 0.5, b * 0.5, theta):
			e = Ellipse((x, y), a_ , b_ , np.rad2deg(t_))
			e.set_clip_box(ax.bbox)
			e.set_alpha(0.4)
			ax.add_artist(e)
		plt.xlim(-0.05,1.05)
		plt.ylim(-0.05,1.05)
		plt.xlabel("X image")
		plt.ylabel("Y image")
		plt.title("image space (exaggerated)")
		
		# Plotting the FWHM
		ax = plt.subplot(133, aspect='equal')
		plt.scatter(XY[:,0], XY[:,1], s=r*200., c=r, edgecolors="None")
		cb = plt.colorbar()
		plt.xlabel("X image")
		plt.ylabel("Y image")
		cb.set_label('FWHM ["]')
		ax.set_xlim([-0.05, 1.05])
		ax.set_ylim([-0.05, 1.05])
		
		if outdir is None:
			plt.show()
		else:
			pltfn = os.path.join(outdir, "psf_field.png")
			if not os.path.exists(outdir):
				os.makedirs(outdir)
			fig.savefig(pltfn)
			logger.info("Saved PSF plots to {}".format(pltfn))
if __name__ == "__main__":
	# This is a demo of how the class PSF field works
	
	import pylab as plt
	from matplotlib.patches import Ellipse
	
	# Selecting a Euclid-like field
	fieldnum = 0
	
	# Iterating over all field types
	for kind in ["e1e2", "e1", "e2", "fwhm", "radial", "tangential", "euclid-like"]:
		
		# The Euclid-like field requires a filepath...
		if kind is "euclid-like":
			kwargs = {"fieldfname": "./psf_fields_euclid/field-{:03d}.pkl".format(fieldnum)}
		else:
			kwargs = {}
		
		# Generating the field
		field = PSF_Field(kind, **kwargs)

		# You could change here the randomly chose fwhm and e:
		# field.e = 0.01

		print "**", kind, "**"
		print "e:", field.e
		print "r:", field.fwhm

		# We call some plots		
		field.plot()

