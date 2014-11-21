"""
This files holds a user-defined measfct.
This way the user has maximum freedom to tweak it, without hardcoding.

It's a very good idea to keep this function in a separate module and not in your
script, so that it can be imported by the multiprocessing pool workers that will call,
it without causing any trouble!
"""

import megalut.meas
import megalut.meas.sewfunc


def measfct(img, catalog, psfimg=None, workdir=None, stampsize=None, psfstampsize=None):
	"""
	This function is custom-made for the MegaLUT GREAT3 wrapper, and it accepts those
	keywords that great3.meas_obs() and great3.meas_sim() will pass to it.
	All other keyword arguments can directly be set in the function calls below.
	"""
	
	# We run galsim_adamom :
	outcat = megalut.meas.galsim_adamom.measure(img, catalog, stampsize=stampsize, measuresky=True)
	
	# We run SExtractor, **starting from the output of the previous shape measurement**
	outcat = megalut.meas.sewfunc.measure(img, outcat, workdir=workdir, sexpath="sex")
	
	"""
	# We run FDNT:
	outcat = megalut.meas.fdnt.measure(img, outcat, psfimg, 
		psfxname="psfx", psfyname="psfy", stampsize=stampsize, psfstampsize=psfstamsize, prefix="fdnt_")
	"""
	
	return outcat


