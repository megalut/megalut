"""
Parameters describing how galaxies should be drawn
"""
import megalut.sim
import numpy as np


def contracted_rayleigh(sigma, max_val, p):
	"""
	A distribution with finite support.
	"""
	tmp = np.random.rayleigh(sigma)
	return (tmp / np.power(1 + np.power(tmp / max_val, p), 1.0 / p))


class CGCSersics(megalut.sim.params.Params):

	def stat(self):
		"""
		stat: called for each catalog (stat is for stationnary)
		"""
		
		########## Shear #########
		tru_s1 = np.random.uniform(-0.05, 0.05)
		tru_s2 = np.random.uniform(-0.05, 0.05)	
		tru_mu = 1.0

		snc_type = 20
		
		
		return {
			"tru_s1" : tru_s1, # shear component 1, in "g" convention
			"tru_s2" : tru_s2, # component 2
			"tru_mu" : tru_mu, # magnification
			"snc_type" : snc_type, # The type of shape noise cancellation. 0 means none, n means n-fold
		}
		


	def draw(self, ix, iy, nx, ny):
		"""
		draw: called for each galaxy	
		"""
	
		########## Galaxy ##########
		
		#max_g = 0.6
		#g = np.random.triangular(0.0, max_g, max_g) # This triangular g gives uniform disk (if you want that)
		#theta = 2.0 * np.pi * np.random.uniform(0.0, 1.0)		
		#(tru_g1, tru_g2) = (g * np.cos(2.0 * theta), g * np.sin(2.0 * theta))
		
		g = contracted_rayleigh(0.25, 0.8, 4)
		theta = 2.0 * np.pi * np.random.uniform(0.0, 1.0)		
		(tru_g1, tru_g2) = (g * np.cos(2.0 * theta), g * np.sin(2.0 * theta))
		
		tru_type = 1 # Seric	
		tru_sersicn =  0.5 + (float(iy)/float(ny))**2.0 * 3.0
		
		
		if np.random.uniform() < 0.25:
			tru_flux =  np.random.uniform(70.0, 220.0)
		else:
			tru_flux =  np.random.uniform(10.0, 70.0)

		
		tru_rad = np.random.uniform(0.6, 2.7)
				
		########## Noise ##########
		# GREAT3 has no Poisson noise, just flat Gaussian.
		tru_sky_level = 10.0 #np.random.uniform(10, 15)
		tru_gain = -1.0
		tru_read_noise = 0.0 # No need for additional noise
		
		tru_pixel = -1.0
		
		return { # It's ugly to not directly fill this dict, but this makes it clearer what is actually returned:
					
			"tru_type" : tru_type, # Galaxy profile type. 0 is Gaussian, 1 is Sersic (see sim.params.profile_types)
			"tru_flux" : tru_flux, # in ADU
			#"tru_sigma" : tru_sigma, # Size sigma, used for Gaussians
			"tru_rad" : tru_rad, # Half-light radius, used for Sersics
			"tru_sersicn" : tru_sersicn, # Lower sersic index = less concentrated = lower adamom_rho4
			"tru_g1" : tru_g1,
			"tru_g2" : tru_g2,
			
			"tru_sky_level" : tru_sky_level, # in ADU, just for generating noise, will not remain in the image
			"tru_gain" : tru_gain, # in photons/ADU. Make this negative to have no Poisson noise
			"tru_read_noise" : tru_read_noise, # in photons if gain > 0.0, otherwise in ADU.Set this to zero to have no flat Gaussian noise
			
			"tru_pixel" : tru_pixel, # If positive, adds an extra convolution by that many pixels to the simulation process
			
			
		}
	
