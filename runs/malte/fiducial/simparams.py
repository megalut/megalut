import megalut.sim
import megalut.tools as tl
import numpy as np
import random # np.random.choice is only available for newer numpys...
import os
	

def trunc_gaussian(m, s, minval, maxval):
	"""
	A truncated Gaussian distrib
	"""
	assert maxval > minval
	a, b = (float(minval) - float(m)) / float(s), (float(maxval) - float(m)) / float(s)
	distr = scipy.stats.truncnorm(a, b, loc=m, scale=s)
	return distr.rvs()


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


def psf_field_1(x, y):
	"""
	A simple PSF "model": this function returns PSF parameters as function of the (x, y) position
	in a plane defined by x and y in [0, 1].
	We also return the equivalent a, b, theta, which is only used for making plots.
	
	We use the definition "varepsilon" of the paper, equivalent to "g" in galsim. g = (a-b)/(a+b), and (a+b)/2 = sigma
	"""
	
	g_amp = 0.25 # maximum g
	default_sigma = 2.0 # average sigma
	sigma_amp = 0.25 # maximum deviation from default sigma
	
	tru_psf_g1 = g_amp * 2.0 * (x - 0.5)
	tru_psf_g2 = g_amp * y
	tru_psf_sigma = default_sigma + sigma_amp * ((x + y) - 1.0) 
	
	tru_psf_g = np.hypot(tru_psf_g1, tru_psf_g2)
	tru_psf_a = tru_psf_sigma * (1.0 + tru_psf_g)
	tru_psf_b = tru_psf_sigma * (1.0 - tru_psf_g)
	tru_psf_theta = np.arctan2(tru_psf_g2, tru_psf_g1) / 2.0
	
	return {"tru_psf_x":x, "tru_psf_y":y, 
		"tru_psf_sigma":tru_psf_sigma, "tru_psf_g1":tru_psf_g1, "tru_psf_g2":tru_psf_g2, "tru_psf_g":tru_psf_g,
		"tru_psf_a":tru_psf_a, "tru_psf_b":tru_psf_b, "tru_psf_theta":tru_psf_theta
		}
	


class Fiducial(megalut.sim.params.Params):
	"""
	Fiducial parameters
	"""
	
	def __init__(self, name=None, snc_type=1, shear=0, noise_level=1.0, min_tru_rad=2.0, min_tru_sb=1.0, varpsf_type=None):
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
		self.noise_level = noise_level # So the default is Gaussian noise with std of 1.0
		self.min_tru_rad = min_tru_rad
		self.min_tru_sb = min_tru_sb
		self.varpsf_type = varpsf_type

	def draw_constants(self):
		"""
		Settings that don't change
		"""
		
		tru_type = 1 # Sersic
		snc_type = self.snc_type # The type of shape noise cancellation. 0 means none, n means n-fold
		tru_sky_level = 0.0 # GREAT3 has no Poisson noise, just flat Gaussian. # in ADU, just for generating noise, will not remain in the image
		tru_gain = -1.0 # in photons/ADU. Make this negative to have no Poisson noise
		tru_read_noise = self.noise_level
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
		if self.varpsf_type is None:
			tru_psf_sigma = 2.0 # -> FWHM = 4.7 pixels
			tru_psf_g1 = 0.0
			tru_psf_g2 = 0.0
			return {"tru_psf_sigma":tru_psf_sigma, "tru_psf_g1":tru_psf_g1, "tru_psf_g2":tru_psf_g2}
		else:
			# We draw a random position on the chip seen as plane with x and y in [0, 1]
			tru_psf_x = np.random.uniform(0.0, 1.0)
			tru_psf_y = np.random.uniform(0.0, 1.0)
			# From this position, we compute a g1, g2 and sigma of the PSF
			
			if self.varpsf_type is 1:
				return psf_field_1(tru_psf_x, tru_psf_y)
			else:
				raise NotImplemented()

	def stat(self):
		"""
		Called for each catalog (stat is for stationnary)
		"""
		return self.draw_constants()


	def draw(self, ix, iy, nx, ny):
		"""
		Called for each galaxy	
		"""
		
		tru_g = trunc_rayleigh(0.2, 0.6)
		tru_theta = 2.0 * np.pi * np.random.uniform(0.0, 1.0)		
		(tru_g1, tru_g2) = (tru_g * np.cos(2.0 * tru_theta), tru_g * np.sin(2.0 * tru_theta))
		
		tru_sersicn = random.choice(np.linspace(1, 4, 10))
		
		tru_sb = np.random.uniform(self.min_tru_sb, 15.0)
		tru_rad = np.random.uniform(self.min_tru_rad, 8.0)
		
		tru_flux = np.pi * tru_rad * tru_rad * tru_sb
			
		out = { # It's ugly to not directly fill this dict, but this makes it clearer what is actually returned:
			"tru_flux":tru_flux,
			"tru_rad":tru_rad,
			"tru_g1":tru_g1,
			"tru_g2":tru_g2,
			"tru_sersicn":tru_sersicn,
			"tru_g":tru_g,
			"tru_theta":tru_theta,
			"tru_sb": tru_sb,
			
		}
		
		out.update(self.draw_s()) # Here the shear gets drawn for each "galaxy"
		out.update(self.draw_psf()) # Idem, random for each galaxy
		out.update(self.draw_constants())
		
		return out
		


class Fiducial_statshear(Fiducial):
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
				
