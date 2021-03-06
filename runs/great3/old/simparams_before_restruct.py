"""
Parameters describing how galaxies should be drawn
"""
import megalut.sim
import numpy as np



class G3CGCSersics(megalut.sim.params.Params):
	"""
	Sersic profiles for GREAT3 training, validation, and tests.
	"""

	def __init__(self, name=None, snc_type=1, shear=0, noise_level=1, distmode="G3", obstype="ground"):
		"""
		- distmode switches between different parameter distributions
		- obstype also affects parameter distributiosn
		"""
		megalut.sim.params.Params.__init__(self)
		if name is not None:
			self.name = name
		self.snc_type = snc_type
		self.shear = shear
		self.noise_level = noise_level # 0.92 is for subfield 99 CGC
		self.distmode = distmode
		self.obstype = obstype
		

	def stat(self):
		"""
		stat: called for each catalog (stat is for stationnary)
		"""
		
		return {"snc_type":self.snc_type} # The type of shape noise cancellation. 0 means none, n means n-fold
		


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
		tru_type = 1 # Seric

		if self.distmode == "G3":
		
			# Simple distributions roughly tuned to ressemble GREAT3
			tru_g = contracted_rayleigh(0.2, 0.7, 4)
			tru_theta = 2.0 * np.pi * np.random.uniform(0.0, 1.0)		
			(tru_g1, tru_g2) = (tru_g * np.cos(2.0 * tru_theta), tru_g * np.sin(2.0 * tru_theta))
			
			if self.obstype == "ground":
				tru_rad = np.random.uniform(0.1, 3.0)
				tru_sb = np.random.normal(1.5, 0.3)
				tru_sersicn =  0.5 + (float(iy)/float(ny))**2 * 2.0
				tru_flux = 2.0 * np.pi * tru_rad * tru_rad * tru_sb # The 2 is from *half*-light-radius
				if tru_flux < 5: # Just a trick, as those don't exist in GREAT3 and are barely detected
					tru_flux *= 10.0
	
			elif self.obstype == "space":
				tru_rad = np.random.uniform(0.1, 10.0)
				tru_sb = np.random.normal(0.2, 0.05)
				tru_sersicn =  0.5 + (float(iy)/float(ny))**2 * 3.5
				tru_flux = 2.0 * np.pi * tru_rad * tru_rad * tru_sb # The 2 is from *half*-light-radius
	
		elif self.distmode == "uni":

			# More "uniform" distribs for nicer filling in plots
			tru_g1 = np.random.uniform(-0.7, 0.7)
			tru_g2 = np.random.uniform(-0.7, 0.7)
			tru_g = np.hypot(tru_g1, tru_g2)
			tru_theta = 0.0	
			tru_sersicn =  0.5 + (float(iy)/float(ny)) * 3.5
			
			if self.obstype == "ground":
				# Used for first training:
				#tru_rad = np.random.uniform(0.5, 3.0)
				#tru_sb = np.random.uniform(2.0, 5.0)
				#tru_flux = 2.0 * np.pi * tru_rad * tru_rad * tru_sb # The 2 is from *half*-light-radius
				tru_rad = np.random.uniform(0.1, 3.0)
				tru_sb = np.random.uniform(0.8, 2.3)
				tru_flux = 2.0 * np.pi * tru_rad * tru_rad * tru_sb # The 2 is from *half*-light-radius
				if tru_flux < 5: # Just a trick, as those don't exist in GREAT3 and are barely detected
					tru_flux *= 10.0
	
			
			elif self.obstype == "space":
				tru_rad = np.random.uniform(0.1, 10.0)
				tru_sb = np.random.uniform(0.15, 0.3)
				tru_flux = 2.0 * np.pi * tru_rad * tru_rad * tru_sb # The 2 is from *half*-light-radius

		
		else:
			raise RuntimeError("Unknown distmode.")
		

		########## Noise ##########
		
		# GREAT3 has no Poisson noise, just flat Gaussian.
		tru_sky_level = 0.0 #np.random.uniform(10, 15)
		tru_gain = -1.0
		tru_read_noise = self.noise_level
		tru_pixel = -1.0
		
		return { # It's ugly to not directly fill this dict, but this makes it clearer what is actually returned:
			"tru_s1" : tru_s1, # shear component 1, in "g" convention
			"tru_s2" : tru_s2, # component 2
			"tru_mu" : tru_mu, # magnification
				
			"tru_type" : tru_type, # Galaxy profile type. 0 is Gaussian, 1 is Sersic (see sim.params.profile_types)
			"tru_flux" : tru_flux, # in ADU
			#"tru_sigma" : tru_sigma, # Size sigma, used for Gaussians
			"tru_rad" : tru_rad, # Half-light radius, used for Sersics
			"tru_sersicn" : tru_sersicn, # Lower sersic index = less concentrated = lower adamom_rho4
			"tru_g1" : tru_g1,
			"tru_g2" : tru_g2,
			"tru_g" : tru_g,
			"tru_theta" : tru_theta,
			"tru_sb" : tru_sb,
			
			"tru_sky_level" : tru_sky_level, # in ADU, just for generating noise, will not remain in the image
			"tru_gain" : tru_gain, # in photons/ADU. Make this negative to have no Poisson noise
			"tru_read_noise" : tru_read_noise, # in photons if gain > 0.0, otherwise in ADU.Set this to zero to have no flat Gaussian noise
			
			"tru_pixel" : tru_pixel, # If positive, adds an extra convolution by that many pixels to the simulation process
			
		}
	


class G3CGCSersics_statshear(G3CGCSersics):
	"""
	To train weights for shear: constant shear per catalog
	"""
	
	def __init__(self, **kwargs):
		G3CGCSersics.__init__(self, **kwargs)
		
	def stat(self):
		"""
		Supercedes what draw returns, called once for each catalog
		"""
		
		if self.shear > 0:
			tru_s1 = np.random.uniform(-self.shear, self.shear)
			tru_s2 = np.random.uniform(-self.shear, self.shear)	
		else:
			tru_s1 = 0.0
			tru_s2 = 0.0
		tru_mu = 1.0
			
		return {
			"tru_s1" : tru_s1, # shear component 1, in "g" convention
			"tru_s2" : tru_s2, # component 2
			"tru_mu" : tru_mu, # magnification
			"snc_type":self.snc_type
		}
	
	


class G3CGCSersics_statell(G3CGCSersics):
	"""
	To train weights, we need cases of different ellipticity
	This is done by:
	- using stat() to give ellipticity, superceding the ellipticity from draw()
	- 1 rea, snc=1, make lots of catalogs, shear=0
	
	
	Alternative: pick ellipticity on a grid using ix iy or from a given list, and group by g1 g2 ?
	
	"""

	def __init__(self, **kwargs):
		G3CGCSersics.__init__(self, **kwargs)
		
	def stat(self):
		"""
		Supercedes what draw returns, called once for each catalog
		"""
		
		if self.distmode == "G3":
			# Simple distributions roughly tuned to ressemble GREAT3
			tru_g = contracted_rayleigh(0.2, 0.7, 4)
			tru_theta = 2.0 * np.pi * np.random.uniform(0.0, 1.0)		
			(tru_g1, tru_g2) = (tru_g * np.cos(2.0 * tru_theta), tru_g * np.sin(2.0 * tru_theta))
			
		elif self.distmode == "uni":
			# More "uniform" distribs for nicer filling in plots
			tru_g1 = np.random.uniform(-0.7, 0.7)
			tru_g2 = np.random.uniform(-0.7, 0.7)
			tru_g = np.hypot(tru_g1, tru_g2)
			tru_theta = 0.0	
			
		return {
			"tru_g1" : tru_g1,
			"tru_g2" : tru_g2,
			"tru_g" : tru_g,
			"tru_theta" : tru_theta,
			"snc_type":self.snc_type
		}
			
			

def contracted_rayleigh(sigma, max_val, p):
	"""
	A distribution with finite support.
	"""
	tmp = np.random.rayleigh(sigma)
	return (tmp / np.power(1 + np.power(tmp / max_val, p), 1.0 / p))


#class CGCSersics(megalut.sim.params.Params):
#
#
#	def __init__(self):
#		megalut.sim.params.Params.__init__(self)
#		self.snc_type = 1000
#		
#
#	def stat(self):
#		"""
#		stat: called for each catalog (stat is for stationnary)
#		"""
#		
#		########## Shear #########
#		sr = 0.15
#		tru_s1 = np.random.uniform(-sr, sr)
#		tru_s2 = np.random.uniform(-sr, sr)	
#		tru_mu = 1.0
#
#		# For fine tuning sims:
#		#tru_s1 = 0
#		#tru_s2 = 0
#		#snc_type = 1
#		
#		
#		return {
#			"tru_s1" : tru_s1, # shear component 1, in "g" convention
#			"tru_s2" : tru_s2, # component 2
#			"tru_mu" : tru_mu, # magnification
#			"snc_type" : self.snc_type, # The type of shape noise cancellation. 0 means none, n means n-fold
#		}
#		
#
#
#	def draw(self, ix, iy, nx, ny):
#		"""
#		draw: called for each galaxy	
#		"""
#	
#		########## Galaxy ##########
#		
#		#max_g = 0.6
#		#g = np.random.triangular(0.0, max_g, max_g) # This triangular g gives uniform disk (if you want that)
#		#theta = 2.0 * np.pi * np.random.uniform(0.0, 1.0)		
#		#(tru_g1, tru_g2) = (g * np.cos(2.0 * theta), g * np.sin(2.0 * theta))
#		
#		tru_g = contracted_rayleigh(0.25, 0.8, 4)
#		tru_theta = 2.0 * np.pi * np.random.uniform(0.0, 1.0)		
#		(tru_g1, tru_g2) = (g * np.cos(2.0 * theta), g * np.sin(2.0 * theta))
#		
#		tru_type = 1 # Seric	
#		tru_sersicn =  0.5 + (float(iy)/float(ny))**2.0 * 3.0
#		
#		
#		if np.random.uniform() < 0.25:
#			tru_flux =  np.random.uniform(70.0, 220.0)
#		else:
#			tru_flux =  np.random.uniform(10.0, 70.0)
#
#		
#		tru_rad = np.random.uniform(0.6, 2.7)
#				
#		########## Noise ##########
#		# GREAT3 has no Poisson noise, just flat Gaussian.
#		tru_sky_level = 0.0 #np.random.uniform(10, 15)
#		tru_gain = -1.0
#		tru_read_noise = 0.92 #  No need for additional noise 0.92 is for subfield 99
#		
#		tru_pixel = -1.0
#		
#		return { # It's ugly to not directly fill this dict, but this makes it clearer what is actually returned:
#					
#			"tru_type" : tru_type, # Galaxy profile type. 0 is Gaussian, 1 is Sersic (see sim.params.profile_types)
#			"tru_flux" : tru_flux, # in ADU
#			#"tru_sigma" : tru_sigma, # Size sigma, used for Gaussians
#			"tru_rad" : tru_rad, # Half-light radius, used for Sersics
#			"tru_sersicn" : tru_sersicn, # Lower sersic index = less concentrated = lower adamom_rho4
#			"tru_g1" : tru_g1,
#			"tru_g2" : tru_g2,
#			"tru_g" : tru_g,
#			"tru_theta" : tru_theta,
#			
#			"tru_sky_level" : tru_sky_level, # in ADU, just for generating noise, will not remain in the image
#			"tru_gain" : tru_gain, # in photons/ADU. Make this negative to have no Poisson noise
#			"tru_read_noise" : tru_read_noise, # in photons if gain > 0.0, otherwise in ADU.Set this to zero to have no flat Gaussian noise
#			
#			"tru_pixel" : tru_pixel, # If positive, adds an extra convolution by that many pixels to the simulation process
#			
#			
#		}
#	
