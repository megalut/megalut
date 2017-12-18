import megalut.sim
import numpy as np
import random # np.random.choice is only available for newer numpys...

import itertools





class Simple1(megalut.sim.params.Params):
	"""
	No PSF, just plain Gaussians and Gaussian noise
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
	
		########## Noise ##########

		tru_sky_level = 0.0
		tru_gain = -1.0
		tru_read_noise = 1.0
		
		#########  No Lensing
		
		tru_s1 = 0.0
		tru_s2 = 0.0
		tru_mu = 1.0

		
		########## Galaxy ##########
		
		tru_type = 0 # 0 Gaussian, 1 sersic	
		
		#minflux = 100.0
		#maxflux = 1000.0
		#tru_flux = minflux + (maxflux - minflux) * float(ny - iy)/float(ny)
		#tru_flux = [100, 150, 200][iy]
		
		
		refrad = (4.3/2.0)
		#minrad = refrad/2.0
		#maxrad = refrad * 2.0
		#tru_rad = minrad + (maxrad-minrad) * float(ix)/float(nx)
		rads = np.array([0.75*refrad, refrad, 1.5*refrad])
		tru_rad = rads[ix]
		
		fact = 0.54
		fluxes = np.array([rads * flux * fact  for flux in [50, 100, 150, 200]]).transpose()
		#print fluxes.shape
		#exit()
		#fluxes = np.array([100, 150, 200])
		
		tru_flux = fluxes[ix, iy]
		
		
		tru_sigma = tru_rad / 1.1774 # We take Croppers "extension of the source" as the half-light-diameter
		
		
		tru_g = 0.0
		tru_theta = 0.0	
		(tru_g1, tru_g2) = (tru_g * np.cos(2.0 * tru_theta), tru_g * np.sin(2.0 * tru_theta))
		
		tru_g = np.hypot(tru_g1, tru_g2)
			
		
		
		return { # It's ugly to not directly fill this dict, but this makes it clearer what is actually returned:
					
			"tru_type":tru_type,
			"tru_flux":tru_flux,
			"tru_rad":tru_rad,
			"tru_sigma":tru_sigma,
			#"tru_sersicn":tru_sersicn,
			"tru_g1":tru_g1,
			"tru_g2":tru_g2,
			"tru_g":tru_g, # only useful for some plots
			
			"tru_sky_level":tru_sky_level, # in ADU, just for generating noise, will not remain in the image
			"tru_gain":tru_gain, # in photons/ADU. Make this negative to have no Poisson noise
			"tru_read_noise":tru_read_noise, # in photons if gain > 0.0, otherwise in ADU.Set this to zero to have no flat Gaussian noise
			
			"tru_s1":tru_s1,
			"tru_s2":tru_s2,
			"tru_mu":tru_mu,
					
		}


