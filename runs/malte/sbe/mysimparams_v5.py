import megalut.sim
import numpy as np
import random # np.random.choice is only available for newer numpys...

import itertools


def contracted_rayleigh(sigma, max_val, p):
	"""
	A special version, uses "Bryan's formula to rein in large values to be less than the max_val"
	"""
	tmp = np.random.rayleigh(sigma)
	return (tmp / np.power(1 + np.power(tmp / max_val, p), 1.0 / p))




class SBE_v5(megalut.sim.params.Params):
	"""
	
	"""
	
	def __init__(self):
		megalut.sim.params.Params.__init__(self)
				
		
	def set_high_sn(self):
		self.flux_fact = 10.0 # Is used to set the sky level
		self.galaxy_flux_or_SN_dist_params = (4.1, 0.1)
	
	def set_low_sn(self):
		self.flux_fact = 1.0
		self.galaxy_flux_or_SN_dist_params = (3.1, 0.1)
	
	
	
	def stat(self):
		"""
		stat: called for each catalog (stat is for stationnary)
		"""
		
		########## Shear #########
		tru_s = contracted_rayleigh(0.01, 0.9, 4)
		tru_s_theta = 2.0 * np.pi * np.random.uniform(0.0, 1.0)		
		(tru_s1, tru_s2) = (tru_s * np.cos(2.0 * tru_s_theta), tru_s * np.sin(2.0 * tru_s_theta))
	
		tru_mu = 1.0
		
		########## PSF ##########
		
		sample_scale = 0.05
		
		# Size: the true SBE distribution ("LogNormal-Mean")
		psf_stddev_arcsec_dist_params = (-1.07, 0.005)
		tru_psf_sigma = (1.0/sample_scale) * 10 ** (np.random.randn() * psf_stddev_arcsec_dist_params[1] + psf_stddev_arcsec_dist_params[0]) * np.exp(-((psf_stddev_arcsec_dist_params[1] * np.log(10)) ** 2) / 2)
		
		# Ellipticty the true SBE distrib ("contracted Rayleigh")
		psf_g = contracted_rayleigh(0.01, 0.9, 4)
		psf_theta = 2.0 * np.pi * np.random.uniform(0.0, 1.0)		
		(tru_psf_g1, tru_psf_g2) = (psf_g * np.cos(2.0 * psf_theta), psf_g * np.sin(2.0 * psf_theta))
	
		return {
			"tru_s1" : tru_s1,
			"tru_s2" : tru_s2,
			"tru_mu" : tru_mu,
				
			"snc_type" : 1, # The type of shape noise cancellation. 0 means none.
			
			"tru_psf_sigma" : tru_psf_sigma,
			"tru_psf_g1" : tru_psf_g1,
			"tru_psf_g2" : tru_psf_g2
			
			}
	
	
	def draw(self, ix, iy, nx, ny):
		"""
		draw: called for each galaxy
		Gaussian galaxies with gaussian PSFs.
		"""
		
		# In MegaLUT we work in pixels. So we need to take into account
		sample_scale = 0.05
		tru_pixel = 2.0
		
		
		########## Galaxy ##########
		
		tru_type = 0 # Gaussian
		
		# Flux: the true SBE ("LogNormal-Mean") 
		tru_flux = 10 ** (np.random.randn() * self.galaxy_flux_or_SN_dist_params[1] + self.galaxy_flux_or_SN_dist_params[0]) * np.exp(-((self.galaxy_flux_or_SN_dist_params[1] * np.log(10)) ** 2) / 2)
		
		# Size: the true SBE distrib ("LogNormal-Peak")
		galaxy_sigma_arcsec_dist_params = (-0.5, 0.15)
		tru_sigma = (1.0/sample_scale) * 10 ** (np.random.randn() * galaxy_sigma_arcsec_dist_params[1] + galaxy_sigma_arcsec_dist_params[0])
		
		# Ellipticty the true SBE distrib ("contracted Rayleigh") # Note that we do not take into account the shear here!
		g = contracted_rayleigh(0.25, 0.9, 4)
		theta = 2.0 * np.pi * np.random.uniform(0.0, 1.0)		
		(tru_g1, tru_g2) = (g * np.cos(2.0 * theta), g * np.sin(2.0 * theta))
			
		########## Noise (these params are stationary anyway) ##########

		tru_sky_level = self.flux_fact * 3257.0 * (sample_scale)**2 # SBE truth, taking pixel scale into account
		tru_gain = 3.5
		tru_read_noise = 10.2
		
	
			
		return { # It's ugly to not directly fill this dict, but this makes it clearer what is actually returned:
			"tru_type" : tru_type,
			"tru_flux" : tru_flux,
			"tru_sigma" : tru_sigma,
			"tru_g1" : tru_g1,
			"tru_g2" : tru_g2,
			
			"tru_sky_level" : tru_sky_level, # in ADU, just for generating noise, will not remain in the image
			"tru_gain" : tru_gain, # in photons/ADU. Make this negative to have no Poisson noise
			"tru_read_noise" : tru_read_noise, # in photons if gain > 0.0, otherwise in ADU.Set this to zero to have no flat Gaussian noise
			
			"tru_pixel": tru_pixel
			
		}



