import megalut.sim
import numpy as np
import random # np.random.choice is only available for newer numpys...

import itertools





class Simple1(megalut.sim.params.Params):
	"""
	EC Gaussian PSF, and galaxies so that the observed size is 0.43 arcsec...
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
	
		#########  No Lensing
		
		tru_s1 = 0.0
		tru_s2 = 0.0
		tru_mu = 1.0
	
	
		# Params
		
		gain = 3.1 # electrons/ADU
		ron = 4.2 # electrons
		skyback = 22.35 # mag per arcsec2, dominated by zodiacal light
		#zeropoint = 25.9 # mag. Should give SNR 10 when observing with 3 x 565 second exposures.
		
		#zeropoint = 24.7 + float(ny - iy)/float(ny) * 1.0 # mag. Should give SNR 10 when observing with 3 x 565 second exposures.
		zeropoint = 26.8
		
		exptime = 3.0*565.0	# seconds
	
		########## Noise ##########

		tru_sky_level = 0.01 * exptime * 10**((skyback - zeropoint)/(-2.5))  # In ADU per pixel. 0.01 because of the pixel size of 0.1 arcsec. No gain, as in ADU!
		tru_gain = gain
		tru_read_noise = ron
		
		#########  No Lensing
		
		tru_s1 = 0.0
		tru_s2 = 0.0
		tru_mu = 1.0

		
		########## Galaxy ##########
		
		tru_type = 1 # 0 Gaussian, 1 sersic	
		
		tru_mag = 24.5
		#tru_mag = 23.0 + float(ny - iy)/float(ny) * 2.5

		tru_flux = (exptime / gain) * 10**((tru_mag - zeropoint)/(-2.5))

		# For sersic index 2, factor = 1.6
		factor = 3.0
		
		tru_rad = 1.95 * factor
		tru_sersicn = 4.0
		
		# Croppers reference galaxy has an extension of 4.3 pixels, but we don't know exactly what this extension means.
		
		#size_factor = 1.0 # scales the galaxy with respect to Croppers reference
		
		#tru_sigma = size_factor * (4.3/2.0) / 1.1774 # We take Croppers "extension of the source" as the half-light-diameter
		#tru_sersicn = 4.0
		
		#tru_cropper_snr = (tru_flux) / np.sqrt( np.pi * (size_factor * 13.0/2.0)**2 * tru_sky_level) # For a sky-limited obs, we don't use the gain here
		
		tru_g = 0.0
		tru_theta = 0.0	
		(tru_g1, tru_g2) = (tru_g * np.cos(2.0 * tru_theta), tru_g * np.sin(2.0 * tru_theta))
		
		tru_g = np.hypot(tru_g1, tru_g2)
			
		
		
		return { # It's ugly to not directly fill this dict, but this makes it clearer what is actually returned:
					
			"tru_type":tru_type,
			"tru_flux":tru_flux,
			"tru_mag":tru_mag,
			"zeropoint":zeropoint,
			"skyback":skyback,
			"tru_rad":tru_rad,
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
			
			#"tru_cropper_snr":tru_cropper_snr,
			
			
		}


