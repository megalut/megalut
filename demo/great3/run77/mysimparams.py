"""
Let's keep those definitions out of the scripts, 
"""
import megalut.sim


class ground_v1(megalut.sim.params.Params):
	"""
	Some attempt reasonably close to "control ground" branches
	"""
	
	def getrad(self):
		return np.random.uniform(0.7, 2.7)
	
	def getflux(self):
		if np.random.uniform() < 0.25:
			return np.random.uniform(70.0, 220.0)
		else:
			return np.random.uniform(10.0, 70.0)
	
	def getg(self):
		theta = np.random.uniform(0.0, 2.0* np.pi) 
		eps = np.random.uniform(0.0, 0.7) 
		return (eps * np.cos(2.0 * theta), eps * np.sin(2.0 * theta))
	  
	def getsersicn(self, ix=0, iy=0, n=1):
		return 1.0 + (float(iy)/float(n)) * 2.0    
		# Lower sersic index = broader

