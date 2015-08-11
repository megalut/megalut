import megalut.sim
import numpy as np
import random # np.random.choice is only available for newer numpys...

import itertools

class SBE_v1(megalut.sim.params.Params):
	
	
	def set_high_sn(self):
		self.flux_fact = 100.0
	
	def set_low_sn(self):
		self.flux_fact = 1.0
	
	
	def draw(self, ix, iy, n):
		"""
		Gaussian galaxies with gaussian PSFs.
		"""
		
		# In MegaLUT we work in pixels. So we need to take into account
		sample_scale = 0.05
		# ... from the SBE.
		
		########## Galaxy ##########
		
		tru_type = 0 # Gaussian
		tru_flux =  self.flux_fact * np.random.uniform(100.0, 600.0) # To be adjusted
		
		# Size: the true SBE distrib ("LogNormal-Peak")
		galaxy_sigma_arcsec_dist_params = (-0.5, 0.15)
		tru_sigma = (1.0/sample_scale) * 10 ** (np.random.randn() * galaxy_sigma_arcsec_dist_params[1] + galaxy_sigma_arcsec_dist_params[0])
		
		# Ellipticty: adjusted from measurements
		max_g = 0.7
		g = np.random.triangular(0.0, max_g, max_g) # This triangular g gives uniform disk (if you want that)
		theta = 2.0 * np.pi * np.random.uniform(0.0, 1.0)		
		(tru_g1, tru_g2) = (g * np.cos(2.0 * theta), g * np.sin(2.0 * theta))
			
		########## Noise ##########

		tru_sky_level = self.flux_fact * 100.0 * (sample_scale)**2 # SBE truth, taking pixel scale into account
		tru_gain = 1.7
		tru_read_noise = 0.3
		
		########## PSF ##########
		
		# Size: first test: let's use the true SBE distribution ("LogNormal-Mean")
		psf_stddev_arcsec_dist_params = (-1.07, 0.005)
		tru_psf_sigma = (1.0/sample_scale) * 10 ** (np.random.randn() * psf_stddev_arcsec_dist_params[1] + psf_stddev_arcsec_dist_params[0]) * np.exp(-((psf_stddev_arcsec_dist_params[1] * np.log(10)) ** 2) / 2)
		
		# It's weird to use the true size distribution here. Given that we do not measure the PSF anyway, we could just use uniform sizes.
		
		tru_pixel = 2.0
		
		max_psf_g = 0.035 # Guessed from observed distribution, did not look at exact SBE config:
		psf_g = np.random.triangular(0.0, max_psf_g, max_psf_g)
		psf_theta = 2.0 * np.pi * np.random.uniform(0.0, 1.0)		
		(tru_psf_g1, tru_psf_g2) = (psf_g * np.cos(2.0 * psf_theta), psf_g * np.sin(2.0 * psf_theta))
		
			
		return { # It's ugly to not directly fill this dict, but this makes it clearer what is actually returned:
			"tru_type" : tru_type,
			"tru_flux" : tru_flux,
			"tru_sigma" : tru_sigma,
			"tru_g1" : tru_g1,
			"tru_g2" : tru_g2,
			
			"tru_sky_level" : tru_sky_level, # in ADU, just for generating noise, will not remain in the image
			"tru_gain" : tru_gain, # in photons/ADU. Make this negative to have no Poisson noise
			"tru_read_noise" : tru_read_noise, # in photons if gain > 0.0, otherwise in ADU.Set this to zero to have no flat Gaussian noise
			
			"tru_pixel": tru_pixel,
			
			"tru_psf_sigma" : tru_psf_sigma,
			"tru_psf_g1" : tru_psf_g1,
			"tru_psf_g2" : tru_psf_g2
		}









class SBE_v2(megalut.sim.params.Params):
	
	
	def __init__(self):
		megalut.sim.params.Params.__init__(self)
				
		sr = 0.05
		mur = 0.1
		steps = 11
		(self.tru_s1_vals, self.tru_s2_vals) = np.meshgrid(
			np.linspace(-sr, sr, steps),
			np.linspace(-sr, sr, steps)
			)

		self.tru_s1_vals = self.tru_s1_vals.flatten()
		self.tru_s2_vals = self.tru_s2_vals.flatten()
		self.tru_s_ids = itertools.cycle(np.arange(steps**2)) # The index number we will use to query the values.
		
	
	def set_high_sn(self):
		self.flux_fact = 10.0
		self.galaxy_flux_or_SN_dist_params = (4.1, 0.1)
		raise RuntimeError("Not yet tested!")
	
	def set_low_sn(self):
		self.flux_fact = 1.0
		self.galaxy_flux_or_SN_dist_params = (3.1, 0.1)
	
	
	
	def stat(self):
		"""
		stat: called for each catalog (stat is for stationnary)
		Simple shears, on a grid, instead of picking at random.
		"""
		
		# Leaving these to the integers 0 0 1 means that the "lens" method will not get called.
		
		tru_s_id = next(self.tru_s_ids)
		
		tru_s1 = self.tru_s1_vals[tru_s_id]
		tru_s2 = self.tru_s2_vals[tru_s_id]
		tru_mu = 1.0
		
		snc_type = 1 # 0 means no shape noise cancellation
	
		return {
			"tru_s_id" : tru_s_id,
			"tru_s1" : tru_s1, # shear component 1, in "g" convention
			"tru_s2" : tru_s2, # component 2
			"tru_mu" : tru_mu, # magnification
			"snc_type" : snc_type, # The type of shape noise cancellation. 0 means none.
		}
	
	
	
	
	def draw(self, ix, iy, nx, ny):
		"""
		draw: called for each galaxy
		Gaussian galaxies with gaussian PSFs.
		"""
		
		# In MegaLUT we work in pixels. So we need to take into account
		sample_scale = 0.05
		tru_pixel = 2.0
		
		# ... from the SBE.
		
		########## Galaxy ##########
		
		tru_type = 0 # Gaussian
		
		# Flux: the true SBE ("LogNormal-Mean") 
		tru_flux = self.flux_fact * 10 ** (np.random.randn() * self.galaxy_flux_or_SN_dist_params[1] + self.galaxy_flux_or_SN_dist_params[0]) * np.exp(-((self.galaxy_flux_or_SN_dist_params[1] * np.log(10)) ** 2) / 2)
		
		# Size: the true SBE distrib ("LogNormal-Peak")
		galaxy_sigma_arcsec_dist_params = (-0.5, 0.15)
		tru_sigma = (1.0/sample_scale) * 10 ** (np.random.randn() * galaxy_sigma_arcsec_dist_params[1] + galaxy_sigma_arcsec_dist_params[0])
		
		# Ellipticty the true SBE distrib ("contracted Rayleigh") # Note that we do not take into account the shear here!
		galaxy_shape_1_dist_params = (0.25, 0.9, 4) # sigma, max_val, p
		first_result = np.random.rayleigh(galaxy_shape_1_dist_params[0]) # Generate an initial random Rayleigh variable (copy exactly from Bryan)
        # Transform it via Bryan's formula to rein in large values to be less than the max_val
		g = (first_result / np.power(1 + np.power(first_result / galaxy_shape_1_dist_params[1], galaxy_shape_1_dist_params[2]), 1.0 / galaxy_shape_1_dist_params[2]))
		theta = 2.0 * np.pi * np.random.uniform(0.0, 1.0)		
		(tru_g1, tru_g2) = (g * np.cos(2.0 * theta), g * np.sin(2.0 * theta))
			
		########## Noise ##########

		tru_sky_level = self.flux_fact * 3257.0 * (sample_scale)**2 # SBE truth, taking pixel scale into account
		tru_gain = 3.5
		tru_read_noise = 10.2
		
		########## PSF ##########
		
		# As we do not measure the PSF shapes, it should work even with different PSF distribs !
		
		# Size: the true SBE distribution ("LogNormal-Mean")
		psf_stddev_arcsec_dist_params = (-1.07, 0.005)
		tru_psf_sigma = (1.0/sample_scale) * 10 ** (np.random.randn() * psf_stddev_arcsec_dist_params[1] + psf_stddev_arcsec_dist_params[0]) * np.exp(-((psf_stddev_arcsec_dist_params[1] * np.log(10)) ** 2) / 2)
		
		# Ellipticty the true SBE distrib ("contracted Rayleigh")
		psf_shape_1_dist_params = (0.01, 0.9, 4)
		first_result = np.random.rayleigh(psf_shape_1_dist_params[0]) # Generate an initial random Rayleigh variable (copy exactly from Bryan)
        # Transform it via Bryan's formula to rein in large values to be less than the max_val
		psf_g = (first_result / np.power(1 + np.power(first_result / psf_shape_1_dist_params[1], psf_shape_1_dist_params[2]), 1.0 / psf_shape_1_dist_params[2]))
		psf_theta = 2.0 * np.pi * np.random.uniform(0.0, 1.0)		
		(tru_psf_g1, tru_psf_g2) = (psf_g * np.cos(2.0 * psf_theta), psf_g * np.sin(2.0 * psf_theta))
		
			
		return { # It's ugly to not directly fill this dict, but this makes it clearer what is actually returned:
			"tru_type" : tru_type,
			"tru_flux" : tru_flux,
			"tru_sigma" : tru_sigma,
			"tru_g1" : tru_g1,
			"tru_g2" : tru_g2,
			
			"tru_sky_level" : tru_sky_level, # in ADU, just for generating noise, will not remain in the image
			"tru_gain" : tru_gain, # in photons/ADU. Make this negative to have no Poisson noise
			"tru_read_noise" : tru_read_noise, # in photons if gain > 0.0, otherwise in ADU.Set this to zero to have no flat Gaussian noise
			
			"tru_pixel": tru_pixel,
			
			"tru_psf_sigma" : tru_psf_sigma,
			"tru_psf_g1" : tru_psf_g1,
			"tru_psf_g2" : tru_psf_g2
		}

