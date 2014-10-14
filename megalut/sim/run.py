"""
High-level functions to make a whole set of simulations.
These functions write their results to disk, and therefore define a directory structure
containing the different realizations, catalogs, etc.
"""


def multi(params, ncpu=4, simdir="sim"):
	"""
	
	Uses stampgrid.drawcat and stampgrid.drawimg to get several catalogs
	and several realizations per catalog.
	We support multiprocessing!
	
	
	:param params: a sim.Params instance that defines the distributions of parameters
	
	:param ncpu: limit to the number of processes I should use.
	
	:param simdir: path to a directory where I should write the simulations.
		This directory has *not* to be unique for every call of this function!
		I will make subdirectories reflecting the name of your params inside.
	
	
	
	"""
