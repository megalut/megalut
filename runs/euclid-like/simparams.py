import megalut.sim
import megalut.tools as tl
import numpy as np
import random # np.random.choice is only available for newer numpys...
import os
import includes
from simparamscomputation import skypropreties as sky

class EuclidLike_Ell(megalut.sim.params.Params):
	
	def __init__(self):
		megalut.sim.params.Params.__init__(self)
		# It's nice to have some params here as attributes, as this allows them to be modified for different sims.
		self.snc_type = 1
		self.shear = 0.0
		self.noise_factor = 1.


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

		if self.shear > 0:
			tru_s1 = np.random.uniform(-self.shear, self.shear)
			tru_s2 = np.random.uniform(-self.shear, self.shear)	
		else:
			tru_s1 = 0.0
			tru_s2 = 0.0
		tru_mu = 1.0
	
		########## Galaxy ##########
		
		# Ellipticities
		tru_g = sky.draw_ellipticities(size=1)
		
		tru_theta = 2.0 * np.pi * np.random.uniform(0.0, 1.0)		
		(tru_g1, tru_g2) = (tru_g * np.cos(2.0 * tru_theta), tru_g * np.sin(2.0 * tru_theta))
		
		# Profile
		tru_type = 1 # Seric	
		tru_sersicn = sky.draw_sersicn(size=1)[0]
		
		# mag
		tru_mag = sky.draw_magnitudes(size=1, mmin=20, mmax=24)	
		zeropoint = includes.zeropoint
		exposuretime = 565.
		tru_flux = 10**(-0.4 * (tru_mag - zeropoint)) * exposuretime / np.abs(includes.gain)

		# Size
		tru_rad = sky.draw_halflightradius(tru_mag)
			
		########## Noise ##########

		tru_sky_level = sky.get_sky(zodical_mag=22.4, exposure=exposuretime, zeropoint=zeropoint, gain=np.abs(includes.gain), pixel_scale=0.1)
		tru_gain = includes.gain
		tru_read_noise = 4.2 * self.noise_factor
		
		return { # It's ugly to not directly fill this dict, but this makes it clearer what is actually returned:
					
			"tru_type":tru_type,
			"tru_flux":tru_flux,
			"tru_rad":tru_rad,
			"tru_g1":tru_g1,
			"tru_g2":tru_g2,
			"tru_sersicn":tru_sersicn,
			"tru_g":tru_g,
			"tru_theta":tru_theta,
			"tru_mag": tru_mag,
			
			"tru_sky_level":tru_sky_level, # in ADU, just for generating noise, will not remain in the image
			"tru_gain":tru_gain, # in photons/ADU. Make this negative to have no Poisson noise
			"tru_read_noise":tru_read_noise, # in photons if gain > 0.0, otherwise in ADU.Set this to zero to have no flat Gaussian noise
			
			"tru_s1":tru_s1,
			"tru_s2":tru_s2,
			"tru_mu":tru_mu,
		}

class Calc_Zerop(EuclidLike_Ell):
	
	def __init__(self, zeropoint):
		EuclidLike_Ell.__init__(self)
		# It's nice to have some params here as attributes, as this allows them to be modified for different sims.
		self.snc_type = 1
		self.zeropoint = zeropoint

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

		if self.shear > 0:
			tru_s1 = np.random.uniform(-self.shear, self.shear)
			tru_s2 = np.random.uniform(-self.shear, self.shear)	
		else:
			tru_s1 = 0.0
			tru_s2 = 0.0
		tru_mu = 1.0
	
		########## Galaxy ##########
		
		# Ellipticities
		tru_g = sky.draw_ellipticities(size=1)
		
		tru_theta = 2.0 * np.pi * np.random.uniform(0.0, 1.0)		
		(tru_g1, tru_g2) = (tru_g * np.cos(2.0 * tru_theta), tru_g * np.sin(2.0 * tru_theta))
		
		# Profile
		tru_type = 1 # Seric	
		tru_sersicn = sky.draw_sersicn(size=1)[0]
		
		# mag
		tru_mag = np.array([24.5])
		exposuretime = 565.
		tru_flux = 10**(-0.4 * (tru_mag - self.zeropoint)) * exposuretime / np.abs(includes.gain)

		# Size
		tru_rad = np.array([0.43/2.])
		
		# Sky
		tru_sky_level = sky.get_sky(zodical_mag=22.4, exposure=exposuretime, zeropoint=self.zeropoint, gain=np.abs(includes.gain), pixel_scale=0.1)
		
		########## Noise ##########

		tru_gain = includes.gain
		tru_read_noise = 4.2
		
		return { # It's ugly to not directly fill this dict, but this makes it clearer what is actually returned:
					
			"tru_type":tru_type,
			"tru_flux":tru_flux,
			"tru_rad":tru_rad,
			"tru_g1":tru_g1,
			"tru_g2":tru_g2,
			"tru_sersicn":tru_sersicn,
			"tru_g":tru_g,
			"tru_theta":tru_theta,
			"tru_mag": tru_mag,
			
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

