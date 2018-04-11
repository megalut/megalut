"""
Feads a catalog at import and draws from it
"""

import megalut.sim
import numpy as np
import random # np.random.choice is only available for newer numpys...

import config

import itertools
import galsim


def trunc_gaussian(m, s, minval, maxval):
	"""
	A truncated Gaussian distrib
	"""
	assert maxval > minval
	a, b = (float(minval) - float(m)) / float(s), (float(maxval) - float(m)) / float(s)
	distr = scipy.stats.truncnorm(a, b, loc=m, scale=s)
	return distr.rvs()


def clip_gaussian(sigma, maxamp):
	"""
	A truncated Gaussian distrib
	"""
	return np.clip(sigma * np.random.normal(), -maxamp, maxamp)
	



def trunc_rayleigh(sigma, max_val):
	"""
	A truncated Rayleigh distribution
	"""
	assert max_val > sigma
	tmp = max_val + 1.0
	while tmp > max_val:
		tmp = np.random.rayleigh(sigma)
	return tmp


def contracted_rayleigh(sigma, max_val, p):
	"""
	A distribution with finite support.
	"""
	tmp = np.random.rayleigh(sigma)
	return (tmp / np.power(1 + np.power(tmp / max_val, p), 1.0 / p))



# Nico's catalog:

sourcecat = megalut.tools.io.readpickle(config.sourcecat)
noise_sigma = sourcecat.meta["noise_sigma"]



class FromCat(megalut.sim.params.Params):

	
	def __init__(self, name=None, snc_type=1, shear=0, noise_level=1.0):
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
		


	def draw_constants(self):
		"""
		Settings that don't change
		"""
		
		tru_type = 1 # Sersic
		snc_type = self.snc_type # The type of shape noise cancellation. 0 means none, n means n-fold
		tru_sky_level = 0.0 # GREAT3 has no Poisson noise, just flat Gaussian. # in ADU, just for generating noise, will not remain in the image
		tru_gain = -1.0 # in photons/ADU. Make this negative to have no Poisson noise
		tru_read_noise = noise_sigma * self.noise_level # Given that gain is negative, this is in ADU !
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
		Draws the parameters of the PSF
		"""
		
		tru_psf_sigma = -42.0 # We use Nico's special psf anyway
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
		
		source_row = random.choice(sourcecat)
		
		sigma = 0.3
		maxamp = 0.7
		tru_e1 = clip_gaussian(sigma, maxamp)
		tru_e2 = clip_gaussian(sigma, maxamp)
		shear = galsim.Shear(e1=tru_e1, e2=tru_e2)
		tru_g1 = shear.g1
		tru_g2 = shear.g2

		#tru_g1 = source_row["tru_g1"]
		#tru_g2 = source_row["tru_g2"]
		#tru_e1 = source_row["tru_e1"]
		#tru_e2 = source_row["tru_e2"]
		
		tru_flux = source_row["tru_flux"]
		tru_rad = source_row["tru_rad"]
		tru_sersicn = source_row["tru_sersicn"]
		tru_mag = source_row["tru_mag"]
			
		out = { # It's ugly to not directly fill this dict, but this makes it clearer what is actually returned:
			"tru_flux":tru_flux,
			"tru_rad":tru_rad,
			"tru_g1":tru_g1,
			"tru_g2":tru_g2,
			"tru_e1":tru_e1,
			"tru_e2":tru_e2,
			"tru_sersicn":tru_sersicn,
			"tru_mag":tru_mag,
		}
		
		out.update(self.draw_s()) # Here the shear gets drawn for each "galaxy"
		out.update(self.draw_psf()) # Idem, random for each galaxy
		out.update(self.draw_constants())
		
		return out
		

	
	
class FromCat_statshear(FromCat):
	"""
	To train weights for shear: constant shear per catalog
	"""
	
	def __init__(self, **kwargs):
		Fiducial.__init__(self, **kwargs)
		
	def stat(self):
		"""
		Supercedes what draw returns, called once for each catalog
		"""
		out = {}
		out.update(self.draw_s()) # Here, it's called for each catalog, and supercedes the galaxy values.
		out.update(self.draw_psf()) # Idem, one random PSF for each catalog
		out.update(self.draw_constants())
		
		return out
				
