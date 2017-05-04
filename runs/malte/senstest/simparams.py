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

	def __init__(self, name=None, snc_type=1, shear=0, noise_level=1, ecode="ep0", minmag=None):
		"""
		- snc_type is the number of shape noise cancellation rotations
		- shear is the maximum shear to be drawn, 0 for no shear
		- noise_level 1.0 means that the fiducial noise level will be used, 0 means no noise
	
		"""
		megalut.sim.params.Params.__init__(self)
		if name is not None:
			self.name = name
		self.snc_type = snc_type
		self.shear = shear
		self.noise_level = noise_level # relative
		self.ecode = ecode
		self.minmag = minmag
		
		self.ccdgain = 3.3
		
		self.db = megalut.tools.io.readpickle(config.truedistpath) # Reading in the database of true values
		sel = megalut.tools.table.Selector("right_p_of_e", [("is", "ecode", self.ecode)])	
		self.db = sel.select(self.db)
		if self.minmag is not None:
			sel = megalut.tools.table.Selector("minmag", [("min", "magnitude", self.minmag)])	
			self.db = sel.select(self.db)


		# Each ecode has a different:
		# - bulge_axis_ratio (we don't care exactly, it just affects the bulge_ellipticity
		# - disk_height_ratio
		####### ep2 has the highest bulge_axis_ratio (0.8) (closest to 1), giving the lowest ellipticities, and the highest disk_height_ratio (0.3).

	def draw_constants(self):
		"""
		Settings that don't change
		"""
		
		tru_type = 2 # Bulge and Disk
		snc_type = self.snc_type # The type of shape noise cancellation. 0 means none, n means n-fold
		tru_sky_level = 0.0 # GREAT3 has no Poisson noise, just flat Gaussian. # in ADU, just for generating noise, will not remain in the image
		tru_gain = -1.0 # in photons/ADU. Make this negative to have no Poisson noise
		
		tru_read_noise = self.noise_level * np.sqrt((32570.0 / 100.0) / self.ccdgain) # in photons if gain > 0.0, otherwise in ADU. Set this to zero to have no flat Gaussian noise
		
		tru_pixel = -1.0 # If positive, adds an extra convolution by that many pixels to the simulation process
		ccdgain = self.ccdgain
		
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
	
		# We draw one galaxy at random from our database.
		dbrow = self.db[np.random.randint(0, len(self.db))]
	
		# Position angle of galaxy
		tru_theta = dbrow["rotation"]
		
		# Computing the total flux
		m = dbrow["magnitude"]
		exp_time = 565.0 # seconds
		mag_vis_zeropoint = 25.6527 # From Lance's code
		tru_flux = (1.0/self.ccdgain) * exp_time * 10.0 ** (0.4 * (mag_vis_zeropoint - m))
		assert dbrow["bulge_fraction"] >= 0.0 and dbrow["bulge_fraction"] <= 1.0
	

		# Properties of bulge
		tru_bulge_g = dbrow["bulge_ellipticity"]
		tru_bulge_hlr = dbrow["hlr_bulge_arcsec"] * 10.0 # We convert arcsec to pixels
		tru_bulge_flux = dbrow["bulge_fraction"] * tru_flux
		tru_bulge_sersicn = float(dbrow["sersic_index"])
		assert tru_bulge_sersicn == 4.0
		
		# Properites of disk
		tru_disk_tilt = dbrow["tilt"]
		tru_disk_scale_h_over_r = dbrow["disk_height_ratio"]
		tru_disk_hlr = dbrow["hlr_disk_arcsec"] * 10.0 # We convert arcsec to pixels
		tru_disk_flux = (1.0 - dbrow["bulge_fraction"]) * tru_flux
	
		
	
		out = {
			"tru_theta":tru_theta,
			"tru_flux":tru_flux, # Maybe useful for plots to have the total flux as well.
			
			"tru_bulge_g":tru_bulge_g,
			"tru_bulge_sersicn":tru_bulge_sersicn,
			"tru_bulge_hlr":tru_bulge_hlr,
			"tru_bulge_flux":tru_bulge_flux,
			
			"tru_disk_tilt":tru_disk_tilt,
			"tru_disk_scale_h_over_r":tru_disk_scale_h_over_r,
			"tru_disk_hlr":tru_disk_hlr,
			"tru_disk_flux":tru_disk_flux,
			
			# Apart from the megalut params, we also keep some originals, for simobs cross-checks
			"magnitude":dbrow["magnitude"],
			"bulge_ellipticity":dbrow["bulge_ellipticity"],
			"tilt":dbrow["tilt"],
			"hlr_bulge_arcsec":dbrow["hlr_bulge_arcsec"],
			"hlr_disk_arcsec":dbrow["hlr_disk_arcsec"],
			
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



