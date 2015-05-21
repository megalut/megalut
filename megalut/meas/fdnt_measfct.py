"""
This files holds a user-defined measfct.
This way the user has maximum freedom to tweak it, without hardcoding.

It's a very good idea to keep this function in a separate module and not in your
script, so that it can be imported by the multiprocessing pool workers that will call
it without causing any trouble!
"""

import megalut.meas
import megalut.meas.sewfunc
import megalut.meas.sewfunc_psf
import megalut.meas.fdntfunc


def measfct(img, catalog, psfimg, workdir=None, stampsize=None, psfstampsize=None):
	"""
	This function is custom-made for the MegaLUT GREAT3 wrapper, and it accepts those
	keywords that great3.meas_obs() and great3.meas_sim() will pass to it.
	All other keyword arguments can directly be set in the function calls below.
	"""
	
	# Run SExtractor on gals
	sexpath = "sex"
	outcat = megalut.meas.sewfunc.measure(img, catalog, workdir=workdir, sexpath=sexpath, prefix='')

	# Run SExtractor on PSFs
	print
	print "IT BEGINS HERE"
	print

	outcat = megalut.meas.sewfunc_psf.measure(psfimg, outcat, workdir=workdir, sexpath=sexpath)

	# Run FDNT:
	outcat = megalut.meas.fdntfunc.measure(img, outcat, psfimg,
		psfxname="psfx", psfyname="psfy", stampsize=stampsize, psfstampsize=psfstampsize)
	
	return outcat


