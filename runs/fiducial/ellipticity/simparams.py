import megalut.sim
import numpy as np
import random # np.random.choice is only available for newer numpys...


class Ellipticity(megalut.sim.params.Params):
	
	def __init__(self):
		megalut.sim.params.Params.__init__(self)
		# It's nice to have some params here as attributes, as this allows them to be modified for different sims.
		self.snc_type = 1
		self.shear = 0.0
		self.noise_level = 0.8


	def stat(self):
		"""
		stat: called for each catalog (stat is for stationnary)
		"""
		return {"snc_type":self.snc_type}
	
	
	def draw(self, ix, iy, nx, ny):
		"""
		draw: called for each galaxy	
		"""
	
		########## PSF ##########
		
		tru_psf_sigma = 2.0
		tru_psf_g1 = 0.0
		tru_psf_g2 = 0.0
	
	
		########## Shear #########	

		if self.shear > 0:
			tru_s1 = np.random.uniform(-self.shear, self.shear)
			tru_s2 = np.random.uniform(-self.shear, self.shear)	
		else:
			tru_s1 = 0.0
			tru_s2 = 0.0
		tru_mu = 1.0
	
		########## Galaxy ##########
		
		tru_g = contracted_rayleigh(0.2, 0.6, 4) # there is no shear, so let's make it a bit broader
		
		tru_theta = 2.0 * np.pi * np.random.uniform(0.0, 1.0)		
		(tru_g1, tru_g2) = (tru_g * np.cos(2.0 * tru_theta), tru_g * np.sin(2.0 * tru_theta))
		
		tru_type = 1 # Seric	
		tru_sersicn = random.choice(np.concatenate([np.linspace(0.3, 4, 10), np.linspace(0.3, 2, 10)]))
		# TODO: Calibrate this surface brigthness
		surface_brigthness = np.random.normal(1., 0.02)

		tru_rad = np.random.uniform(1.0, 15.0)
		
		tru_flux = np.pi * tru_rad * tru_rad * 10**(-surface_brigthness)
			
		########## Noise ##########

		tru_sky_level = 0.0
		tru_gain = -1.0
		tru_read_noise = self.noise_level * 0.1 ** 2
		
		return { # It's ugly to not directly fill this dict, but this makes it clearer what is actually returned:
					
			"tru_type":tru_type,
			"tru_flux":tru_flux,
			"tru_rad":tru_rad,
			"tru_g1":tru_g1,
			"tru_g2":tru_g2,
			"tru_sersicn":tru_sersicn,
			"tru_g":tru_g,
			"tru_theta":tru_theta,
			"tru_sb": surface_brigthness,
			
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





def contracted_rayleigh(sigma, max_val, p):
	"""
	A distribution with finite support.
	"""
	tmp = np.random.rayleigh(sigma)
	return (tmp / np.power(1 + np.power(tmp / max_val, p), 1.0 / p))


