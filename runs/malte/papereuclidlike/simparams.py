"""
Feads a catalog at import and draws from it
"""

import megalut.sim
import numpy as np
import random # np.random.choice is only available for newer numpys...
import scipy.stats
import config

import itertools
import galsim



def trunc_rayleigh(sigma, max_val):
	"""
	A truncated Rayleigh distribution
	"""
	assert max_val > sigma
	tmp = max_val + 1.0
	while tmp > max_val:
		tmp = np.random.rayleigh(sigma)
	return tmp

def trunc_gaussian(m, s, minval, maxval):
	"""
	A truncated Gaussian distrib
	"""
	assert maxval > minval
	a, b = (float(minval) - float(m)) / float(s), (float(maxval) - float(m)) / float(s)
	distr = scipy.stats.truncnorm(a, b, loc=m, scale=s)
	return distr.rvs()


# Loading the GEMS catalog:

sourcecat = megalut.tools.io.readpickle(config.sourcecat)

# Selections
#sel = megalut.tools.table.Selector("draw", [
#		("in", "tru_mag", 20.5, 24.0),
#	])
#sourcecat = sel.select(sourcecat)


# Euclid params
	
pixel_scale = 0.1 # arcsec per pixel
exptime = 3.0*565.0	# seconds

gain = 3.1 # electrons/ADU
ron = 4.2 # electrons

skyback = 22.35 # mag per arcsec2, dominated by zodiacal light
zeropoint = 24.6 # mag, VIS instrumental


class EuclidLike(megalut.sim.params.Params):

	
	def __init__(self, name=None, snc_type=1, shear=0, noise_level=1.0, dist_type="gems"):
		"""
		- snc_type is the number of shape noise cancellation rotations
		- shear is the maximum shear to be drawn, 0 for no shear
		- noise_level 1.0 means that the fiducial noise level will be used, 0 means no noise
		"""
		
		megalut.sim.params.Params.__init__(self)
		if name is not None:
			self.name = name
		self.snc_type = snc_type
		self.shear = shear
		self.noise_level = noise_level
		self.dist_type = dist_type
		


	def draw_constants(self):
		"""
		Settings that don't change from stamp to stamp
		"""
		
		tru_type = 1 # Sersic
		snc_type = self.snc_type # The type of shape noise cancellation. 0 means none, n means n-fold
		
		tru_sky_level = (pixel_scale)**2 * (exptime/gain) * 10**(-0.4*(skyback - zeropoint)) # in ADU, just for generating noise, will not remain in the image
		
		tru_gain = gain
		tru_read_noise = ron # in e-, given that gain is > 0
		
		tru_pixel = -1.0 # If positive, adds an extra convolution by that many pixels to the simulation process
		
		return {"snc_type":snc_type, "tru_type":tru_type, "tru_sky_level":tru_sky_level,
			"tru_gain":tru_gain, "tru_read_noise":tru_read_noise, "tru_pixel":tru_pixel,
			}


	def draw_s(self):
		"""
		Shear and magnification
		"""
		
		if self.shear > 0.0 and self.shear < 10.0:
			tru_s1 = np.random.uniform(-self.shear, self.shear)
			tru_s2 = np.random.uniform(-self.shear, self.shear)		
		else:
			tru_s1 = 0.0
			tru_s2 = 0.0
		
		tru_mu = 1.0
		return {"tru_s1":tru_s1, "tru_s2":tru_s2, "tru_mu":tru_mu}


	def draw_psf(self):
		"""
		Draws the parameters of the PSF : not used, as , we use an image psf.
		"""
		
		tru_psf_sigma = -1.0
		tru_psf_g1 = 0.0
		tru_psf_g2 = 0.0
		
		return {"tru_psf_sigma":tru_psf_sigma, "tru_psf_g1":tru_psf_g1, "tru_psf_g2":tru_psf_g2}


	def stat(self):
		"""
		Called for each catalog (stat is for stationnary)
		"""
		return self.draw_constants()



	def draw(self, ix, iy, nx, ny):
		"""
		Called for each galaxy	
		"""
		
		#tru_e = trunc_rayleigh(0.25, 0.6)
		#tru_e2 = clip_gaussian(sigma, maxamp)
		#shear = galsim.Shear(e1=tru_e1, e2=tru_e2)
		#tru_g1 = shear.g1
		#tru_g2 = shear.g2
		
		tru_g = trunc_rayleigh(0.25, 0.7) # Follows Hoekstra et al. 2017 and 2015, for the sigma-e (yes, the do use a-b/a+b as def)
		tru_theta = 2.0 * np.pi * np.random.uniform(0.0, 1.0)
		(tru_g1, tru_g2) = (tru_g * np.cos(2.0 * tru_theta), tru_g * np.sin(2.0 * tru_theta))
		
		if self.dist_type == "gems":
			"""
			Takes values from a random GEMS galaxy
			"""
			source_row = random.choice(sourcecat)
			
			tru_rad = source_row["tru_rad"]
			tru_mag = source_row["tru_mag"]
		
			# The sersicn is "tmp", as we discretize it further below
			tru_sersicn_tmp = source_row["tru_sersicn"]
			
			
		elif self.dist_type == "unig":
			"""
			Uniform or very simple distributions
			"""
			tru_rad = np.random.uniform(1.0, 10.0)
			tru_mag = np.random.uniform(20.5, 25.0)
			tru_sersicn_tmp = trunc_gaussian(1.0, 2.5, 0.3, 6.0)
			

		elif self.dist_type == "uni":
			"""
			Uniform only distributions -- can this work ?
			"""
			tru_rad = np.random.uniform(1.0, 10.0)
			tru_mag = np.random.uniform(20.5, 25.0)
			tru_sersicn_tmp = np.random.uniform(0.3, 6.0)

		elif self.dist_type == "uni05":
			"""
			Uniform only distributions -- can this work ?
			"""
			tru_rad = np.random.uniform(0.5, 10.0)
			tru_mag = np.random.uniform(20.5, 25.0)
			tru_sersicn_tmp = np.random.uniform(0.3, 6.0)
			
		
		else:
			raise RuntimeError("Unknown dist_type")
		
		
		tru_flux =  (exptime / gain) * 10**(-0.4*(tru_mag - zeropoint))
		
		# We want a discrete number of sersic indices to keep GalSim efficient, so we approximate it to the closest step:
		tru_sersicns = np.linspace(0.3, 6.0, 21)
		tru_sersicn = tru_sersicns[(np.abs(tru_sersicns-tru_sersicn_tmp)).argmin()]
		
		out = { # It's ugly to not directly fill this dict, but this makes it clearer what is actually returned:
			"tru_flux":tru_flux,
			"tru_rad":tru_rad,
			"tru_g1":tru_g1,
			"tru_g2":tru_g2,
			"tru_g":tru_g,
			"tru_theta":tru_theta,
			"tru_sersicn":tru_sersicn,
			"tru_mag":tru_mag,
		}
		
		out.update(self.draw_s()) # Here the shear gets drawn for each "galaxy"
		out.update(self.draw_psf()) # Idem, random for each galaxy
		out.update(self.draw_constants())
		
		return out
		

	
	
class EuclidLike_statshear(EuclidLike):
	"""
	To train weights for shear: constant shear per catalog
	"""
	
	def __init__(self, **kwargs):
		EuclidLike.__init__(self, **kwargs)
		
	def stat(self):
		"""
		Supercedes what draw returns, called once for each catalog
		"""
		out = {}
		out.update(self.draw_s()) # Here, it's called for each catalog, and supercedes the galaxy values.
		out.update(self.draw_psf()) # Idem, one random PSF for each catalog
		out.update(self.draw_constants())
		
		return out
			
				
