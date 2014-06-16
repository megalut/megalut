import numpy as np
import math

class SimParams:
	"""
	A container for the parameters describing the drawing of a *set* of simulated galaxies.
	To use it, you inherit this class and overload its minimal methods (if desired)
	Only the method "get" gets called by the simulation code.
	For full control, simply override this "get" !
	"""
	
	def __init__(self):
		self.sig = 9999.0 
			# The sky noise.
			# This value will get set by the code at a later stage.
			
		
	def getsig(self):
		return self.sig
	
	def getrad(self):
		return np.random.uniform(0.5, 5.0)
		
	def getflux(self):
		return np.random.uniform(10.0, 200.0)
		
	
	def getsersicn(self, ix=0, iy=0, n=1):
		"""
		A bit special, as we do not want to simply randomize the sersic index,
		as this would terribly slow down galsim.
		"""
		pseudorand = float(iy)/float(n)
		return 0.5 + pseudorand * 3.0
		
	
	def getg(self):
		return np.random.uniform(low=-0.65, high=0.65, size=2)
		
	
	def get(self, ix, iy, n):
		"""
		Call this function to get some (random) parameters to draw your galaxy.
		This is the only function that gets called when drawing a galaxy !
		You can of course also override this method if you want e.g. correlated params !
		
		ix and iy are the indices of the galaxy, going from 0 to n-1.
		This can be used to generate parameters, instead of just drawing them randomly.
		"""
		
		(g1, g2) = self.getg()
		
		return {
			"sig" : self.getsig(),
			"rad" : self.getrad(),
			"flux" : self.getflux(),
			"sersicn" : self.getsersicn(ix=ix, iy=iy, n=n),
			"g1" : g1,
			"g2" : g2
		}


			

class OldMalteGroundSimParams(SimParams):
	"""
	This is related to GREAT3 and should therefore not be here, but it just serves as a demo.
	Here we overload the intividual parameters.
	"""


	def getrad(self):
		return np.random.uniform(0.7, 2.7)
	
	def getflux(self):
		if np.random.uniform() < 0.25:
			return np.random.uniform(70.0, 220.0)
		else:
			return np.random.uniform(10.0, 70.0)
	
	def getg(self):
		theta = np.random.uniform(0.0, 2.0* math.pi) 
		eps = np.random.uniform(0.0, 0.7) 
		return (eps * np.cos(2.0 * theta), eps * np.sin(2.0 * theta))
		
	def getsersicn(self, ix=0, iy=0, n=1):
		return 1.0 + (float(iy)/float(n)) * 2.0	
		# Lower sersic index = broader
		



class OldMalteSpaceSimParams(SimParams):
	"""
	Similar, but we overload the get method instead.
	"""

	def get(self, ix, iy, n):
		
		
		if np.random.uniform() > 0.5:
			rad = 1.0 + 9.0*np.random.uniform()
		else:
			rad = 1.0 + 4.0*np.random.uniform()
				
		if np.random.uniform() > 0.75:
			flux = 8.0 + 140.0*np.random.uniform()
		else:
			flux = 8.0 + 45.0*np.random.uniform()
			
		if rad > 5.0 and np.random.uniform() > 0.5:
			flux *= 2.0
		if rad < 5.0 and np.random.uniform() > 0.5:
			flux /= 2.0
			
		(g1, g2) = np.random.uniform(low=-0.6, high=0.6, size=2)
				
		pseudorand = float(iy)/float(n)
		if pseudorand < 0.8:
			sersicn = 0.5 + pseudorand * 1.25
		else:
			normpseudorand = (pseudorand - 0.8)/0.2
			sersicn = 1.0 + normpseudorand * 2.0
		# Lower sersic index = broader, do not randomize becasue of GalSim efficiency !

		return {
			"sig" : self.getsig(),
			"rad" : rad,
			"flux" : flux,
			"sersicn" : sersicn,
			"g1" : g1,
			"g2" : g2
		}


	

