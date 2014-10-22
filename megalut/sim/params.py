import numpy as np
import math

class Params:
	"""
	A container for the distributions describing the parameters of a simulated galaxy.
	To use it, you inherit this class and override its methods as desired.
	Only the method "get" gets called by the simulation code. Hence, instead of overriding all the "get_xxx" methods, you can also simply override this "get".
	
	The minimal methods implemented here are just examples.	Example how you could inherit and override this:
	
	>>> class Flux120(megalut.sim.params.Params):
	>>> 	def get_flux(self):
	>>> 		return 120.0
	>>> 	
	>>> simparams = Flux120()

	
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
	
		self.sig = 1.0 
		# The sky noise.
		# If you do now overwrite get_sig, you will have to set this value at some point.
	
	def __str__(self):
		return "[sim.Params '%s']" % (self.name)
		
	def get_sig(self):
		return self.sig
	
	def get_rad(self):
		return np.random.uniform(0.5, 5.0)
		
	def get_flux(self):
		return np.random.uniform(10.0, 200.0)
		
	def get_sersicn(self, ix=0, iy=0, n=1):
		"""
		This is a bit special: we do not draw sersic indices randomly, as changing it from stamp to stamp significantly slows down galsim ! That's why we need to know the stamp index.

		:param ix: x index of the galaxy, going from 0 to n-1
		:param iy: y index, idem
		:param n: n x n is the number of stamps
		
		"""
		pseudorand = float(iy)/float(n)
		return 0.5 + pseudorand * 3.0
		
	def get_g(self):
		return np.random.uniform(low=-0.4, high=0.4, size=2)
		
	def get(self, ix, iy, n):
		"""
		This is the method that gets called to generate a catalog of simulated galaxies.
		"""
		
		(g1, g2) = self.get_g()
		
		return {
			"tru_sig" : self.get_sig(),
			"tru_rad" : self.get_rad(),
			"tru_flux" : self.get_flux(),
			"tru_sersicn" : self.get_sersicn(ix=ix, iy=iy, n=n),
			"tru_g1" : g1,
			"tru_g2" : g2
		}


			

	

