import megalut.sim
import numpy as np
import random # np.random.choice is only available for newer numpys...

import itertools


def contracted_rayleigh(sigma, max_val, p):
	"""
	A distribution with finite support.
	"""
	tmp = np.random.rayleigh(sigma)
	return (tmp / np.power(1 + np.power(tmp / max_val, p), 1.0 / p))




class GauShear1(megalut.sim.params.Params):
	"""
	Gaussians with shear.
	Single PSF.
	"""
	
	def stat(self):
		"""
		stat: called for each catalog (stat is for stationnary)
		"""
		return {"snc_type":1}
	
	
	def draw(self, ix, iy, nx, ny):
		"""
		draw: called for each galaxy	
		"""
	
		########## Shear #########
		#tru_s = contracted_rayleigh(0.01, 0.9, 4)
		#tru_s_theta = 2.0 * np.pi * np.random.uniform(0.0, 1.0)		
		#(tru_s1, tru_s2) = (tru_s * np.cos(2.0 * tru_s_theta), tru_s * np.sin(2.0 * tru_s_theta))
	
		tru_s1 = np.random.uniform(-0.05, 0.05)
		tru_s2 = np.random.uniform(-0.05, 0.05)	
		tru_mu = 1.0

		########## PSF ##########
		
		tru_psf_sigma = 2.0
		
		# Ellipticty the true SBE distrib ("contracted Rayleigh")
		#psf_g = contracted_rayleigh(0.01, 0.9, 4)
		#psf_theta = 2.0 * np.pi * np.random.uniform(0.0, 1.0)		
		#(tru_psf_g1, tru_psf_g2) = (psf_g * np.cos(2.0 * psf_theta), psf_g * np.sin(2.0 * psf_theta))
	
		tru_psf_g1 = 0.0
		tru_psf_g2 = 0.0
	
		########## Galaxy ##########
		
		tru_type = 0 # Gaussian	
		tru_flux = np.random.uniform(1000.0, 10000.0)
		tru_sigma = np.random.uniform(2.0, 10.0)
		
		# Ellipticty the true SBE distrib ("contracted Rayleigh") # Note that we do not take into account the shear here!
		g = contracted_rayleigh(0.25, 0.9, 4)
		theta = 2.0 * np.pi * np.random.uniform(0.0, 1.0)		
		(tru_g1, tru_g2) = (g * np.cos(2.0 * theta), g * np.sin(2.0 * theta))
			
		########## Noise ##########

		tru_sky_level = 10.0
		tru_gain = 1.0
		tru_read_noise = 2.0
		
		return { # It's ugly to not directly fill this dict, but this makes it clearer what is actually returned:
					
			"tru_type":tru_type,
			"tru_flux":tru_flux,
			"tru_sigma":tru_sigma,
			"tru_g1":tru_g1,
			"tru_g2":tru_g2,
			
			"tru_sky_level":tru_sky_level, # in ADU, just for generating noise, will not remain in the image
			"tru_gain":tru_gain, # in photons/ADU. Make this negative to have no Poisson noise
			"tru_read_noise":tru_read_noise, # in photons if gain > 0.0, otherwise in ADU.Set this to zero to have no flat Gaussian noise
			
			"tru_s1":tru_s1,
			"tru_s2":tru_s2,
			"tru_mu":tru_mu,
			
			"tru_psf_sigma":tru_psf_sigma,
			"tru_psf_g1":tru_psf_g1,
			"tru_psf_g2":tru_psf_g2,
			
		}


