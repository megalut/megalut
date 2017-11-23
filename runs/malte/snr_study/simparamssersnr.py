import megalut.sim
import numpy as np
import random # np.random.choice is only available for newer numpys...

import itertools





class Simple1(megalut.sim.params.Params):
	"""
	No PSF, just round Gaussians
	"""
	
	
	def __init__(self):
		megalut.sim.params.Params.__init__(self)

	
	def stat(self):
		"""
		stat: called for each catalog (stat is for stationnary)
		"""
		return {"snc_type":1}
	
	
	def draw(self, ix, iy, nx, ny):
		"""
		draw: called for each galaxy	
		"""
		
		
		gain = 3.1 # electrons/ADU
		ron = 4.2 # electrons
		skyback = 22.35 # mag per arcsec2, dominated by zodiacal light
		#zeropoint = 25.9 # mag. Should give SNR 10 when observing with 3 x 565 second exposures.
		
		zeropoint = 25.9
		
		exptime = 3.0*565.0	# seconds
		
		#########  No Lensing

		tru_sky_level = 0.01 * exptime * 10**((skyback - zeropoint)/(-2.5))  # In ADU per pixel. 0.01 because of the pixel size of 0.1 arcsec. No gain, as in ADU!
		tru_gain = gain
		tru_read_noise = ron
		
		#########  No Lensing
		
		tru_s1 = 0.0
		tru_s2 = 0.0
		tru_mu = 1.0



		
		########## Galaxy ##########
		
		tru_type = 1 # 0 Gaussian, 1 sersic
		tru_sersicn = 2.0
		
		
		#tru_mag = 24.5
		tru_mag = 23.0 + float(iy)/float(ny) * 2.5

		tru_flux = (exptime / gain) * 10**((tru_mag - zeropoint)/(-2.5))

		
		#factor = 3.2 # for serscin 4
		factor = 1.4 # for serscin 2
		#factor = 1.0 # for sersic 1
		tru_rad = factor * 4.3/2.0
		
		tru_g = 0.0
		tru_theta = 0.0	
		(tru_g1, tru_g2) = (tru_g * np.cos(2.0 * tru_theta), tru_g * np.sin(2.0 * tru_theta))
		
		tru_g = np.hypot(tru_g1, tru_g2)
			
		
		
		return { # It's ugly to not directly fill this dict, but this makes it clearer what is actually returned:
					
			"tru_type":tru_type,
			"tru_flux":tru_flux,
			"tru_rad":tru_rad,
			"tru_mag":tru_mag,
			"zeropoint":zeropoint,
			#"tru_sigma":tru_sigma,
			"tru_sersicn":tru_sersicn,
			"tru_g1":tru_g1,
			"tru_g2":tru_g2,
			"tru_g":tru_g, # only useful for some plots
			
			"tru_sky_level":tru_sky_level, # in ADU, just for generating noise, will not remain in the image
			"tru_gain":tru_gain, # in photons/ADU. Make this negative to have no Poisson noise
			"tru_read_noise":tru_read_noise, # in photons if gain > 0.0, otherwise in ADU.Set this to zero to have no flat Gaussian noise
			
			"tru_s1":tru_s1,
			"tru_s2":tru_s2,
			"tru_mu":tru_mu,
			
			"tru_psf_sigma":0.75,
			"tru_psf_g1":0.0,
			"tru_psf_g2":0.0,

			
		}


