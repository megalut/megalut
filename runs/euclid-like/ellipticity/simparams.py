import megalut.sim
import megalut.tools as tl
import numpy as np
import random # np.random.choice is only available for newer numpys...
import os
import config
from sky import skypropreties as sky

import logging
logger = logging.getLogger(__name__)

simdir = config.simdir

class EuclidLike_Ell(megalut.sim.params.Params):
	
	def __init__(self, galdb):
		megalut.sim.params.Params.__init__(self)
		# It's nice to have some params here as attributes, as this allows them to be modified for different sims.
		self.snc_type = 1
		self.shear = 0.0
		self.noise_factor = 1.
		self.galdb = galdb
		
		self.row_init = np.random.randint(0, len(self.galdb))
		self.row = self.row_init
		
		logger.debug("Class {} has been loaded, with row init {}/{}".format(self.__class__.__name__, self.row, len(self.galdb)))


	def stat(self):
		"""
		stat: called for each catalog (stat is for stationnary)
		"""
		return {"snc_type":self.snc_type}
	
	
	def draw(self, ix, iy, nx, ny):
		"""
		draw: called for each galaxy	
		"""
		
		dbrow = self.galdb[self.row]
		self.row += 1
		if self.row >= len(self.galdb):
			self.row = 0
		
		if self.row == self.row_init:
			logger.warning("Used all galaxies in DB ({} gals), starting again".format(len(self.galdb)))
		
	
		########## Shear #########	

		if self.shear > 0:
			tru_s1 = np.random.uniform(-self.shear, self.shear)
			tru_s2 = np.random.uniform(-self.shear, self.shear)	
		else:
			tru_s1 = 0.0
			tru_s2 = 0.0
		tru_mu = 1.0
	
		########## Galaxy ##########
		
		# Profile
		tru_type = 1 # Seric	
			
		########## Noise ##########

		tru_sky_level = sky.get_sky(zodical_mag=config.skylevel, exposure=config.exposuretime, zeropoint=config.zeropoint, gain=np.abs(config.gain), pixel_scale=config.pixelscale)
		tru_gain = config.gain
		tru_read_noise = config.read_noise * self.noise_factor
		
		return { # It's ugly to not directly fill this dict, but this makes it clearer what is actually returned:
					
			"tru_type":tru_type,
			"tru_flux":dbrow['flux'],
			"tru_rad":dbrow['rad'],
			"tru_g1":dbrow['g1'],
			"tru_g2":dbrow['g2'],
			"tru_sersicn":dbrow['sersicn'],
			"tru_g":dbrow['g'],
			"tru_theta":dbrow['theta'],
			"tru_mag": dbrow['mag'],
			
			"tru_sky_level":tru_sky_level, # in ADU, just for generating noise, will not remain in the image
			"tru_gain":tru_gain, # in photons/ADU. Make this negative to have no Poisson noise
			"tru_read_noise":tru_read_noise, # in photons if gain > 0.0, otherwise in ADU.Set this to zero to have no flat Gaussian noise
			
			"tru_s1":tru_s1,
			"tru_s2":tru_s2,
			"tru_mu":tru_mu,
		}

class Calc_Zerop(EuclidLike_Ell):
	
	def __init__(self, zeropoint):
		megalut.sim.params.Params.__init__(self)
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
		tru_flux = 10**(-0.4 * (tru_mag - self.zeropoint)) * config.exposuretime / np.abs(config.gain)

		# Size
		tru_rad = np.array([0.43/2.])
		
		# Sky
		tru_sky_level = sky.get_sky(zodical_mag=config.skylevel, exposure=config.exposuretime, zeropoint=self.zeropoint, gain=np.abs(config.gain), pixel_scale=config.pixelscale)
		
		########## Noise ##########

		tru_gain = config.gain
		tru_read_noise = config.read_noise
		
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
			
			"tru_s1":0.,
			"tru_s2":0.,
			"tru_mu":1.,
		}
		

class Default(megalut.sim.params.Params):
	
	def __init__(self, galdb):
		megalut.sim.params.Params.__init__(self)
		# It's nice to have some params here as attributes, as this allows them to be modified for different sims.
		self.snc_type = 1
		self.shear = 0.0
		self.noise_factor = 1.
		self.galdb = galdb
		
		self.row_init = np.random.randint(0, len(self.galdb))
		self.row = self.row_init
		
		logger.debug("Class {} has been loaded, with row init {}/{}".format(self.__class__.__name__, self.row, len(self.galdb)))


	def stat(self):
		"""
		stat: called for each catalog (stat is for stationnary)
		"""
		return {"snc_type":self.snc_type}
	
	
	def draw(self, ix, iy, nx, ny):
		"""
		draw: called for each galaxy	
		"""
		
		dbrow = self.galdb[self.row]
		self.row += 1
		if self.row >= len(self.galdb):
			self.row = 0
		
		if self.row == self.row_init:
			logger.warning("Used all galaxies in DB ({} gals), starting again".format(len(self.galdb)))
		
	
		########## Shear #########	

		if self.shear > 0:
			tru_s1 = np.random.uniform(-self.shear, self.shear)
			tru_s2 = np.random.uniform(-self.shear, self.shear)	
		else:
			tru_s1 = 0.0
			tru_s2 = 0.0
		tru_mu = 1.0
	
		########## Galaxy ##########
		
		# Profile
		tru_type = 1 # Seric	
			
		########## Noise ##########

		tru_sky_level = sky.get_sky(zodical_mag=config.skylevel, exposure=config.exposuretime, zeropoint=config.zeropoint, gain=np.abs(config.gain), pixel_scale=config.pixelscale)
		tru_gain = config.gain
		tru_read_noise = config.read_noise * self.noise_factor
		
		return { # It's ugly to not directly fill this dict, but this makes it clearer what is actually returned:
					
			"tru_type":tru_type,
			"tru_flux":dbrow['flux'],
			"tru_rad":dbrow['rad'],
			"tru_g1":dbrow['g1'],
			"tru_g2":dbrow['g2'],
			"tru_sersicn":dbrow['sersicn'],
			"tru_g":dbrow['g'],
			"tru_theta":dbrow['theta'],
			"tru_mag": dbrow['mag'],
			"tru_sb": dbrow['surface_brigthness'],
			
			"tru_sky_level":tru_sky_level, # in ADU, just for generating noise, will not remain in the image
			"tru_gain":tru_gain, # in photons/ADU. Make this negative to have no Poisson noise
			"tru_read_noise":tru_read_noise, # in photons if gain > 0.0, otherwise in ADU.Set this to zero to have no flat Gaussian noise
			
			"tru_s1":tru_s1,
			"tru_s2":tru_s2,
			"tru_mu":tru_mu,
		}
		
