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
	A clipped Gaussian distrib, which Nico is in fact using
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

	
	def __init__(self, name=None, snc_type=1, shear=0, noise_level=1.0, dist_type="cat", e_type=1, e_maxamp=0.9):
		"""
		- snc_type is the number of shape noise cancellation rotations
		- shear is the maximum shear to be drawn, 0 for no shear
		- noise_level 1.0 means that the fiducial noise level will be used, 0 means no noise
		
		- e_type is the kind of ellipticity distribution to use:
			1 : a flawed way, for the June 2018 run
			2 : a better way, for the Sep 2018 run
			
		"""
		
		megalut.sim.params.Params.__init__(self)
		if name is not None:
			self.name = name
		self.snc_type = snc_type
		self.shear = shear
		self.noise_level = noise_level
		self.dist_type = dist_type
		
		self.e_type = e_type
		self.e_maxamp = e_maxamp
		if self.e_maxamp > 0.8:
			raise RuntimeError("We decided with Nico on 2018-09-10 that we should cut at 0.7 to avoid ugly galaxies, but I only redo the weight training.")


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
		
		if self.e_type == 1:
			# This is what Nico was doing for the first tests. Yes, indeed, clip_gaussian.
			
			raise RuntimeError("Should no longer be used")
			sigma = 0.3 # par composante
			maxamp = 0.7
			tru_e1 = clip_gaussian(sigma, maxamp)
			tru_e2 = clip_gaussian(sigma, maxamp)
			shear = galsim.Shear(e1=tru_e1, e2=tru_e2)
			tru_g1 = shear.g1
			tru_g2 = shear.g2
			
			
		elif self.e_type == 2:
			
			tru_g = trunc_rayleigh(0.26, self.e_maxamp) # Agreed with Nico and Tim
			tru_theta = 2.0 * np.pi * np.random.uniform(0.0, 1.0)
			(tru_g1, tru_g2) = (tru_g * np.cos(2.0 * tru_theta), tru_g * np.sin(2.0 * tru_theta))
			shear = galsim.Shear(g1=tru_g1, g2=tru_g2)
			tru_e1 = shear.e1
			tru_e2 = shear.e2
	
		else:
			raise RuntimeError("Unknown e_type")
		
		if self.dist_type == "cat":
			"""
			This mimics Nico's simulations of bright galaxies
			"""
			
			source_row = random.choice(sourcecat)
			
			tru_flux = source_row["tru_flux"]
			tru_rad = source_row["tru_rad"]
			tru_sersicn = source_row["tru_sersicn"]
			tru_mag = source_row["tru_mag"]
			tru_sb = 0.0
		
		elif self.dist_type == "uni":
			"""
			For training the point estimators, simpler uniform sims
			"""
			"""
			tru_g = np.random.uniform(0.0, 0.7)
			tru_theta = 2.0 * np.pi * np.random.uniform(0.0, 1.0)		
			(tru_g1, tru_g2) = (tru_g * np.cos(2.0 * tru_theta), tru_g * np.sin(2.0 * tru_theta))
			tru_e1 = 0.0
			tru_e2 = 0.0
			"""
			
			tru_sersicn = random.choice(np.concatenate([np.linspace(0.3, 6.2, 5), np.linspace(0.5, 1.5, 10)]))
			tru_sb = np.random.uniform(2.0, 50.0)
			tru_rad = np.random.uniform(1.0, 12.0)
			tru_flux = np.pi * tru_rad * tru_rad * tru_sb
			tru_mag = 0.0
		
		elif self.dist_type == "uni2":
			"""
			Simpler
			"""	
			tru_sersicn_tmp = trunc_gaussian(1.0, 2.5, 0.3, 6.0)
			# We want discrete sersic indices, so we approximate this to the closest steop:
			tru_sersicns = np.linspace(0.3, 6.0, 30)
			tru_sersicn = tru_sersicns[(np.abs(tru_sersicns-tru_sersicn_tmp)).argmin()]
			
			tru_rad = np.random.uniform(2.0, 10.0)
			t_exp = 3*565.0 # s
			gain = 3.1 # e-/ADU
			ZP = 24.14
			tru_mag = np.random.uniform(20.5, 24.5)
			tru_flux =  t_exp * 10**(-0.4 * (tru_mag - ZP)) / gain # ADU
			tru_sb = 0.0
		
		else:
			raise RuntimeError("Unknown dist_type")
		
	
			
		out = { # It's ugly to not directly fill this dict, but this makes it clearer what is actually returned:
			"tru_flux":tru_flux,
			"tru_rad":tru_rad,
			"tru_g1":tru_g1,
			"tru_g2":tru_g2,
			"tru_e1":tru_e1,
			"tru_e2":tru_e2,
			"tru_sersicn":tru_sersicn,
			"tru_mag":tru_mag,
			"tru_sb":tru_sb
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
		FromCat.__init__(self, **kwargs)
		
	def stat(self):
		"""
		Supercedes what draw returns, called once for each catalog
		"""
		out = {}
		out.update(self.draw_s()) # Here, it's called for each catalog, and supercedes the galaxy values.
		out.update(self.draw_psf()) # Idem, one random PSF for each catalog
		out.update(self.draw_constants())
		
		return out
			
				
