import megalut.sim
import numpy as np
import random # np.random.choice is only available for newer numpys...

import itertools


class Nico2(megalut.sim.params.Params):
	"""
	Nico's Euclid-like PSF (special implementation)
	Sersic Galaxies
	Simple shear, with SNC
	"""
	
	def __init__(self):
		megalut.sim.params.Params.__init__(self)
		snc_type = 100


	def stat(self):
		"""
		stat: called for each catalog (stat is for stationnary)
		"""
		return {"snc_type":self.snc_type}
	
	
	def draw(self, ix, iy, nx, ny):
		"""
		draw: called for each galaxy	
		"""
	
		########## Shear #########
		#tru_s = contracted_rayleigh(0.01, 0.9, 4)
		#tru_s_theta = 2.0 * np.pi * np.random.uniform(0.0, 1.0)		
		#(tru_s1, tru_s2) = (tru_s * np.cos(2.0 * tru_s_theta), tru_s * np.sin(2.0 * tru_s_theta))
	
		sr = 0.15
		tru_s1 = np.random.uniform(-sr, sr) # Yes, trying something huge to see how that goes when predicting smaller shears
		tru_s2 = np.random.uniform(-sr, sr)	
		tru_mu = 1.0

		########## PSF ##########
		
		#tru_psf_sigma = 2.0
		
		# Ellipticty the true SBE distrib ("contracted Rayleigh")
		#psf_g = contracted_rayleigh(0.01, 0.9, 4)
		#psf_theta = 2.0 * np.pi * np.random.uniform(0.0, 1.0)		
		#(tru_psf_g1, tru_psf_g2) = (psf_g * np.cos(2.0 * psf_theta), psf_g * np.sin(2.0 * psf_theta))
	
		#tru_psf_g1 = 0.0
		#tru_psf_g2 = 0.0
	
		########## Galaxy ##########
		
		g = contracted_rayleigh(0.25, 0.65, 4)
		theta = 2.0 * np.pi * np.random.uniform(0.0, 1.0)		
		(tru_g1, tru_g2) = (g * np.cos(2.0 * theta), g * np.sin(2.0 * theta))
		
		tru_type = 1 # Seric	
		#tru_sersicn =  0.5 + (float(iy)/float(ny))**2.0 * 3.0
		tru_sersicn =  0.5 + (float(iy)/float(ny)) * 5.0
		tru_sersicn = random.choice(np.concatenate([np.linspace(0.3, 4, 10), np.linspace(0.3, 2, 10)]))
		
		if np.random.uniform(0.0, 1.0) < 0.35:
			tru_flux =  np.random.uniform(10, 100.0)
		else:
			tru_flux =  np.random.uniform(2.0, 10.0)

		tru_rad = np.random.uniform(1.0, 15.0)
			
		########## Noise ##########

		tru_sky_level = 0.0
		tru_gain = -1.0
		tru_read_noise = 0.8 * 0.1 ** 2
		
		return { # It's ugly to not directly fill this dict, but this makes it clearer what is actually returned:
					
			"tru_type":tru_type,
			"tru_flux":tru_flux,
			"tru_rad":tru_rad,
			"tru_g1":tru_g1,
			"tru_g2":tru_g2,
			"tru_sersicn":tru_sersicn,
			
			"tru_sky_level":tru_sky_level, # in ADU, just for generating noise, will not remain in the image
			"tru_gain":tru_gain, # in photons/ADU. Make this negative to have no Poisson noise
			"tru_read_noise":tru_read_noise, # in photons if gain > 0.0, otherwise in ADU.Set this to zero to have no flat Gaussian noise
			
			"tru_s1":tru_s1,
			"tru_s2":tru_s2,
			"tru_mu":tru_mu,
		
		}





def contracted_rayleigh(sigma, max_val, p):
	"""
	A distribution with finite support.
	"""
	tmp = np.random.rayleigh(sigma)
	return (tmp / np.power(1 + np.power(tmp / max_val, p), 1.0 / p))


