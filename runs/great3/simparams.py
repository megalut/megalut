"""
Parameters describing how galaxies should be drawn
"""
import megalut.sim
import numpy as np
import scipy.stats



class G3Sersics(megalut.sim.params.Params):
	"""
	Sersic profiles for GREAT3 training, validation, and tests.
	"""

	def __init__(self, name=None, snc_type=1, shear=0, noise_level=1, distmode="G3", obstype="ground"):
		"""
		- snc_type is the number of shape noise cancellation rotations
		- shear is the maximum shear to be drawn, 0 for no shear
		- noise_level > 0 means that the subfields noise level will be used, 0 means no noise
		- distmode switches between different parameter distributions
		- obstype also affects parameter distributions to match the different G3 branches ("ground" or "space")
		"""
		megalut.sim.params.Params.__init__(self)
		if name is not None:
			self.name = name
		self.snc_type = snc_type
		self.shear = shear
		self.noise_level = noise_level
		self.distmode = distmode
		self.obstype = obstype
		

	def draw_s(self):
		"""
		Shear and magnification
		"""
		if self.shear > 0:
			tru_s1 = np.random.uniform(-self.shear, self.shear)
			tru_s2 = np.random.uniform(-self.shear, self.shear)	
			
			#tru_s = 0.1
			#tru_theta = 2.0 * np.pi * np.random.uniform(0.0, 1.0)	
			#(tru_s1, tru_s2) = (tru_s * np.cos(2.0 * tru_theta), tru_s * np.sin(2.0 * tru_theta))
			
		else:
			tru_s1 = 0.0
			tru_s2 = 0.0
		
		tru_mu = 1.0
		return {"tru_s1":tru_s1, "tru_s2":tru_s2, "tru_mu":tru_mu}


	def draw_g(self):
		"""
		Galaxy ellipticity
		"""
		if self.distmode == "G3" or self.distmode == "train":
			# Simple distributions roughly tuned to ressemble GREAT3
			tru_g = contracted_rayleigh(0.2, 0.7, 4)
			tru_theta = 2.0 * np.pi * np.random.uniform(0.0, 1.0)		
			(tru_g1, tru_g2) = (tru_g * np.cos(2.0 * tru_theta), tru_g * np.sin(2.0 * tru_theta))
		
		elif self.distmode == "uni":
			# More "uniform" distribs for nicer filling in plots
			tru_g1 = np.random.uniform(-0.7, 0.7)
			tru_g2 = np.random.uniform(-0.7, 0.7)
			tru_g = np.hypot(tru_g1, tru_g2)
			tru_theta = 0.0 # Not needed, in fact.
			
		return {"tru_g1":tru_g1, "tru_g2":tru_g2, "tru_g":tru_g, "tru_theta":tru_theta}


	def draw_rad(self):
		"""
		Galaxy half-light-radius
		"""
		if self.distmode == "G3":

			if self.obstype == "ground":
				tru_rad = trunc_gaussian(1.0, 0.8, 0.75, 3.0)
			elif self.obstype == "space":
				#tru_rad = trunc_gaussian(3.0, 2.4, 2.25, 9.0) # Just a factor 3 larger than "ground", given that it's in pixels.
				tru_rad = trunc_gaussian(2.5, 3.5, 1.25, 10.0)
		
		elif self.distmode == "uni":
			
			if self.obstype == "ground":
				tru_rad = np.random.uniform(0.1, 3.0)
			elif self.obstype == "space":
				tru_rad = np.random.uniform(0.1, 10.0)
				
		elif self.distmode == "train": # Avoid the hopelessly small galaxies
		
			if self.obstype == "ground":
				tru_rad = np.random.uniform(0.75, 3.0)
			elif self.obstype == "space":
				tru_rad = np.random.uniform(1.25, 10.0)
		
		return {"tru_rad":tru_rad}
		
		
	def draw_sersicn(self, iy, ny):
		"""
		Galaxy Sersic index
		For GalSim performance it's better to not draw them completely randomly over the field.
		- iy: index of the y position in the field
		- ny: maximum index of the y position in the field
		"""
		if self.distmode == "G3": # Note the power 2, seems more representative
			
			if self.obstype == "ground":
				tru_sersicn =  0.5 + (float(iy)/float(ny))**2 * 2.0
			elif self.obstype == "space":
				tru_sersicn =  0.5 + (float(iy)/float(ny))**2 * 3.5
				
		elif self.distmode == "uni" or self.distmode == "train":
		
			tru_sersicn =  0.5 + (float(iy)/float(ny)) * 3.5
				
		return {"tru_sersicn":tru_sersicn}


	def draw_sb(self):
		"""
		Galaxy surface brightness
		Note that this is not used for GREAT3.
		"""
		
#		if self.distmode == "G3":
#			
#			if self.obstype == "ground":		
#				tru_sb = np.random.normal(1.5, 0.75)
#			elif self.obstype == "space":	
#				tru_sb = np.random.normal(0.2, 0.05)
#		
#		elif self.distmode == "uni" or self.distmode == "train":
#			
#			if self.obstype == "ground":				
#				tru_sb = np.random.uniform(0.8, 2.3)
#			elif self.obstype == "space":
#				tru_sb = np.random.uniform(0.15, 0.30)
		
		tru_sb = -1.0
		return {"tru_sb":tru_sb}


	def draw_flux(self):
		"""
		Galaxy flux
		"""
	
		if self.distmode == "G3":
			
			if self.obstype == "ground":
				tru_flux = trunc_gaussian(15, 20, 10, 200)		
				
			elif self.obstype == "space":	
				tru_flux = trunc_gaussian(0, 30, 10, 200)
		
		elif self.distmode == "uni":
		
			if self.obstype == "ground":				
				tru_flux = np.random.uniform(5, 80)
				
			elif self.obstype == "space":
				tru_flux = np.random.uniform(5, 80)
		
		
		elif self.distmode == "train":
			
			if self.obstype == "ground":				
				tru_flux = np.random.uniform(10, 100)
				
			elif self.obstype == "space":
				tru_flux = np.random.uniform(10, 100)
	
	
		return {"tru_flux":tru_flux}


	def draw_constants(self):
		"""
		Settings that don't change
		"""
		
		tru_type = 1 # 1 means Seric
		snc_type = self.snc_type # The type of shape noise cancellation. 0 means none, n means n-fold
		tru_sky_level = 0.0 # GREAT3 has no Poisson noise, just flat Gaussian. # in ADU, just for generating noise, will not remain in the image
		tru_gain = -1.0 # in photons/ADU. Make this negative to have no Poisson noise
		tru_read_noise = self.noise_level # in photons if gain > 0.0, otherwise in ADU. Set this to zero to have no flat Gaussian noise
		tru_pixel = -1.0 # If positive, adds an extra convolution by that many pixels to the simulation process

		return {"snc_type":snc_type, "tru_type":tru_type, "tru_sky_level":tru_sky_level,
			"tru_gain":tru_gain, "tru_read_noise":tru_read_noise, "tru_pixel":tru_pixel}


	def stat(self):
		"""
		Called for each catalog (stat is for stationnary)
		"""
			
		return self.draw_constants()
		


	def draw(self, ix, iy, nx, ny):
		"""
		Called for each galaxy	
		"""
	
		if self.distmode not in ["G3", "uni", "train"]:
			raise RuntimeError("Unknown distmode.")
		
		out = {}
		out.update(self.draw_s())
		out.update(self.draw_g())
		out.update(self.draw_rad())
		out.update(self.draw_sb())
		out.update(self.draw_flux())
		out.update(self.draw_sersicn(iy, ny))
		
		
		# We no longer use SB for GREAT3
		#out["tru_flux"] = 2.0 * np.pi * out["tru_rad"] * out["tru_rad"] * out["tru_sb"] # The 2 is from *half*-light-radius
				
		return out
		
		


class G3Sersics_statshear(G3Sersics):
	"""
	To train weights for shear: constant shear per catalog
	"""
	
	def __init__(self, **kwargs):
		G3Sersics.__init__(self, **kwargs)
		
	def stat(self):
		"""
		Supercedes what draw returns, called once for each catalog
		"""
		
		out = {}
		out.update(self.draw_s())
		out.update(self.draw_constants())
		return out
				
			
			

def trunc_gaussian(m, s, minval, maxval):
	"""
	A truncated Gaussian distrib
	"""
	assert maxval > minval
	a, b = (float(minval) - float(m)) / float(s), (float(maxval) - float(m)) / float(s)
	distr = scipy.stats.truncnorm(a, b, loc=m, scale=s)
	return distr.rvs()



def contracted_rayleigh(sigma, max_val, p):
	"""
	A distribution with finite support.
	"""
	tmp = np.random.rayleigh(sigma)
	return (tmp / np.power(1 + np.power(tmp / max_val, p), 1.0 / p))



