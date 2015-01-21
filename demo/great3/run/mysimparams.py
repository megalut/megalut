"""
Let's keep those definitions out of the scripts, 
"""
import megalut.sim
import numpy as np


class Ground_v1(megalut.sim.params.Params):
	"""
	Some attempt reasonably close to "control ground" branches
	"""
	
	def get_rad(self):
		return np.random.uniform(0.7, 2.7)
	
	def get_flux(self):
		if np.random.uniform() < 0.25:
			return np.random.uniform(70.0, 220.0)
		else:
			return np.random.uniform(10.0, 70.0)
	
	def get_g(self):
		theta = np.random.uniform(0.0, 2.0* np.pi) 
		eps = np.random.uniform(0.0, 0.7) 
		return (eps * np.cos(2.0 * theta), eps * np.sin(2.0 * theta))

	def get_sersicn(self, ix=0, iy=0, n=1):
		return 1.0 + (float(iy)/float(n)) * 2.0    
		# Lower sersic index = broader


ground_v1 = Ground_v1()



class Space_v1(megalut.sim.params.Params):
	"""
	Taken over from MegaLUT v4 runs on CSV:
	"""
	
	def get_rad(self):
		return np.random.uniform(0.5, 12.0)
		
	def get_flux(self):
		return np.random.uniform(8, 40.0) + (np.random.uniform())**5.0 * 100.0
	
	def get_g(self):
		maxg = 0.9
		g = np.random.triangular(0.0, maxg, maxg)
		theta = 2.0 * np.pi * np.random.uniform(0.0, 1.0)		
		return (g * np.cos(2.0 * theta), g * np.sin(2.0 * theta))
	
	def get_sersicn(self, ix=0, iy=0, n=1):
		return 0.3 + (float(iy)/float(n))**3.0 * 4.0
		# Lower sersic index = broader
	

space_v1 = Space_v1()
ground_v1 = Ground_v1()
