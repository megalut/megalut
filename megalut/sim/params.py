import numpy as np
import math


profile_types = ["Gaussian", "Sersic", "EBulgeDisk"] # Order defines the numerical codes of the galaxy profile types
# EBulgeDisk is a simple Bulge + Disk model that we use for some EC tests.


class Params:
	"""
	A container for the distributions describing the parameters of a simulated galaxy.
	To use it, write your own child class (which inherits from this one) and redefine the
	"draw" method as you wish.
	The distributions provided here are really just examples!
	Of course, you are free to add "correlations" between parameters.
	"""
	
	def __init__(self, name=None):
		"""
		:param name: a simple name for your Params object ("test1", "nonoise", "gdisk", ...).
			This name might be used in filenames by pipelines, so keep it short and whitespace-free.
			If None, I will use the name of the class. This is usually exactly what you want, when
			you make your own class LowNoise()
			
		:type name: string
		
		"""
		if name == None:
			self.name = self.__class__.__name__
		else:	
			self.name = name
				
	
	def __str__(self):
		"""
		The string representation is in fact the name:
		"""
		return "%s" % (self.name)

	
	def stat(self):
		"""
		This method returns the "stationnary" parameters, it gets called only *once* per catalog creation.
		
		If you want to override any of the parameters returned by draw() with some stationnary values, just include
		them in the output of this stat()!
		"""
		
		tru_s1 = 0 # Leaving these lensing parameters to the integers 0 0 1 means that the "lens" method will not get called.
		tru_s2 = 0
		tru_mu = 1
		
		snc_type = 0 # 0 means no shape noise cancellation
		
		return {
			"tru_s1" : tru_s1, # shear component 1, in "g" convention
			"tru_s2" : tru_s2, # component 2
			"tru_mu" : tru_mu, # magnification
			"snc_type" : snc_type, # The type of shape noise cancellation. 0 means none, n means n-fold
		}
		
		
	
	def draw(self, ix, iy, nx, ny):
		"""
		The method that gets called to draw the random variables, and which you shoud redefine.
		In the given example, we only draw Sersic profiles, and we do include parameters for Gaussian PSFs.
		
		:param ix: x index of the galaxy, going from 0 to nx-1
		:param iy: idem for y
		:param nx: number of x indexes
		:param ny: idem for y
	
		As you see, this method will know about the "position" of a galaxy on a grid.
		This allows you to generate non-random distributions, using these grid indexes.
		For instance, you should not draw sersic indices randomly,
		as changing it from stamp to stamp significantly slows down galsim !
		
		.. note:: Comments on what to return are included in the example code of this method.
		
		"""
		
		# See the return statement below for comments!
		
		tru_type = 1
		tru_flux =  np.random.uniform(1000.0, 10000.0)
		
		#tru_sigma = np.random.uniform(1.0, 4.0) # For sersic, we do not have to provide this.
		tru_rad = np.random.uniform(1.0, 4.0)
		
		max_g = 0.6
		g = np.random.triangular(0.0, max_g, max_g) # This triangular g gives uniform disk (if you want that)
		theta = 2.0 * np.pi * np.random.uniform(0.0, 1.0)		
		(tru_g1, tru_g2) = (g * np.cos(2.0 * theta), g * np.sin(2.0 * theta))
			
		tru_sersicn =  0.5 + (float(iy)/float(ny))**2.0 * 3.0
		
		tru_sky_level = 100.0
		tru_gain = 1.0
		tru_read_noise = 3.0
		
		tru_pixel = -1.0
		
		tru_psf_sigma = 1.0
		
		max_psf_g = 0.2
		psf_g = np.random.triangular(0.0, max_psf_g, max_psf_g)
		psf_theta = 2.0 * np.pi * np.random.uniform(0.0, 1.0)		
		(tru_psf_g1, tru_psf_g2) = (psf_g * np.cos(2.0 * psf_theta), psf_g * np.sin(2.0 * psf_theta))
			
		return {
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
			
			"tru_psf_sigma" : tru_psf_sigma, # Gaussian PSFs will only be used if no PSF stamps are given
			"tru_psf_g1" : tru_psf_g1, # You don't have to provide those parameters if you will use stamps
			"tru_psf_g2" : tru_psf_g2
		}

