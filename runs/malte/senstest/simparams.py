"""
Parameters describing how galaxies should be drawn
"""
import megalut.sim
import numpy as np
import scipy.stats
import megalut
import config



class SampledBDParams(megalut.sim.params.Params):
	"""
	Bulge and Disk parameters read from a database of samples.
	"""

	def __init__(self, name=None, snc_type=1, shear=0, noise_level=1):
		"""
		- snc_type is the number of shape noise cancellation rotations
		- shear is the maximum shear to be drawn, 0 for no shear
		- noise_level > 0 means that the subfields noise level will be used, 0 means no noise
	
		"""
		megalut.sim.params.Params.__init__(self)
		if name is not None:
			self.name = name
		self.snc_type = snc_type
		self.shear = shear
		self.noise_level = noise_level
		
		self.db = megalut.tools.io.readpickle(config.truedistpath) # Reading in the database of true values
		sel = megalut.tools.table.Selector("right_p_of_e", [("is", "ecode", "ep2")])
		self.db = sel.select(self.db)
	

	def draw_constants(self):
		"""
		Settings that don't change
		"""
		
		tru_type = 2 # Bulge and Disk
		snc_type = self.snc_type # The type of shape noise cancellation. 0 means none, n means n-fold
		tru_sky_level = 0.0 # GREAT3 has no Poisson noise, just flat Gaussian. # in ADU, just for generating noise, will not remain in the image
		tru_gain = -1.0 # in photons/ADU. Make this negative to have no Poisson noise
		tru_read_noise = self.noise_level # in photons if gain > 0.0, otherwise in ADU. Set this to zero to have no flat Gaussian noise
		tru_pixel = -1.0 # If positive, adds an extra convolution by that many pixels to the simulation process
		ccdgain = 3.3
		
		return {"snc_type":snc_type, "tru_type":tru_type, "tru_sky_level":tru_sky_level,
			"tru_gain":tru_gain, "tru_read_noise":tru_read_noise, "tru_pixel":tru_pixel,
			"ccdgain":ccdgain}

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


	def stat(self):
		"""
		Called for each catalog (stat is for stationnary)
		"""
			
		return self.draw_constants()
		


	def draw(self, ix, iy, nx, ny):
		"""
		Called for each galaxy	
		"""
	
		dbrow = self.db[np.random.randint(0, len(self.db))]
	
	
		# Ellipticity of bulge, theta is also used to rotate the disk
		tru_bulge_g = dbrow["bulge_ellipticity"]
		tru_rot = dbrow["rotation"]
		(tru_bulge_g1, tru_bulge_g2) = (tru_bulge_g * np.cos(2.0 * tru_rot), tru_bulge_g * np.sin(2.0 * tru_rot))
	
		#tru_theta = 2.0 * np.pi * np.random.uniform(0.0, 1.0)	
		#(tru_bulge_g1, tru_bulge_g2) = (tru_bulge_g * np.cos(2.0 * tru_theta), tru_bulge_g * np.sin(2.0 * tru_theta))
	
		# Properites of disk
		tru_disk_tilt = dbrow["tilt"]
		tru_disk_scale_h_over_r = dbrow["disk_height_ratio"]
		
		
		# Computing the sizes
		tru_bulge_hlr = dbrow["hlr_bulge_arcsec"] * 10.0 # We work in pixels
		tru_disk_hlr = dbrow["hlr_bulge_arcsec"] * 10.0
	
		# Computing the fluxes
		m = dbrow["magnitude"]
		exp_time = 565.0 # seconds
		mag_vis_zeropoint = 25.6527 # From Lance's code
		tru_flux = exp_time * 10.0 ** (0.4 * (mag_vis_zeropoint - m))
		assert dbrow["bulge_fraction"] >= 0.0 and dbrow["bulge_fraction"] <= 1.0
		tru_bulge_flux = dbrow["bulge_fraction"] * tru_flux
		tru_disk_flux = (1.0 - dbrow["bulge_fraction"]) * tru_flux
	
	
	
		out = {
			"tru_bulge_g1":tru_bulge_g1,
			"tru_bulge_g2":tru_bulge_g2,
			"tru_rot":tru_rot,
		
			"tru_disk_tilt":tru_disk_tilt,
			"tru_disk_scale_h_over_r":tru_disk_scale_h_over_r,
		
			"tru_bulge_hlr":tru_bulge_hlr,
			"tru_disk_hlr":tru_disk_hlr,
			
			"tru_bulge_flux":tru_bulge_flux,
			"tru_disk_flux":tru_disk_flux
			}
		
		out.update(self.draw_s())
		out.update(self.draw_constants())
		
		return out
		


class SampledBDParams_statshear(SampledBDParams):
	"""
	To train weights for shear: constant shear per catalog
	"""
	
	def __init__(self, **kwargs):
		SampledBDParams.__init__(self, **kwargs)
		
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


def trun_rayleigh(sigma, max_val):
	"""
	A truncated Rayleigh distribution
	"""
	assert max_val > sigma
	tmp = max_val + 1.0
	while tmp > max_val:
		tmp = np.random.rayleigh(sigma)
	return tmp


def contracted_rayleigh(sigma, max_val, p):
	"""
	A distribution with finite support.
	"""
	tmp = np.random.rayleigh(sigma)
	return (tmp / np.power(1 + np.power(tmp / max_val, p), 1.0 / p))



