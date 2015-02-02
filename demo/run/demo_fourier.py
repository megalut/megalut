"""
Demo of the "fourier.py" measurement, mainly to explore its speed.

"""

import os
import megalut
import megalut.sim
import megalut.meas

import logging
logging.basicConfig(format='\033[1;31m%(levelname)s\033[1;0m: %(name)s(%(funcName)s): \033[1;21m%(message)s\033[1;0m', level=logging.DEBUG)

#basedir = "/vol/fohlen11/fohlen11_1/mtewes/foo"
basedir = '/tmp/MegaLUT_demo/'

print "Step 1: drawing the sims"

simdir = os.path.join(basedir, "simdir") # Where the simulations should be written

class Flux700(megalut.sim.params.Params):
	def get_flux(self):
		return 700.0 # Low flux, so that we get some failures in this demo.

simparams = Flux700()

"""
# We have to prepare a psfcat
psfcat = megalut.tools.io.readpickle("../generic/psfs/cat_psfgrid.pkl")

# This particular psfcat has no imageinfo yet, so we prepare one from scratch:
psfcat.meta["img"] = megalut.tools.imageinfo.ImageInfo("../generic/psfs/psfgrid.fits", "psfx", "psfy", 32)

drawcatkwargs = {"n":100, "stampsize":32}

megalut.sim.run.multi(simdir, simparams, drawcatkwargs,
	psfcat=psfcat, psfselect="random",
	ncat=1, nrea=1, ncpu=1)

exit()
"""

print "Step 2, measuring"

measdir = os.path.join(basedir, "measdir") # Where the measurements should be written
measfct = megalut.meas.fourier.measfct
measfctkwargs = {}

megalut.meas.run.onsims(simdir, simparams, measdir, measfct, measfctkwargs, ncpu=1, skipdone=False)




exit()

print "Step 3, summarizing measurements accross simulations"

groupcols = [
	"adamom_flux", "adamom_x", "adamom_y", "adamom_g1", "adamom_g2",
	"adamom_sigma", "adamom_rho4",
	"adamom_skystd", "adamom_skymad", "adamom_skymean", "adamom_skymed", "adamom_flag"
	]

removecols=[]

mybigmeascat = megalut.meas.avg.onsims(measdir, simparams,
	groupcols=groupcols,
	removecols=removecols,
	removereas = True
	)

print mybigmeascat["id", "tru_flux", "adamom_flux_mean", "adamom_flux_med", "adamom_flux_std", "adamom_flux_n"]
print mybigmeascat.meta



# If you have installed sewpy, you can replace Steps 2 and 3 by this :
"""

print "Step 2, measuring"

import megalut.meas.sewfunc

measdir = os.path.join(basedir, "measdir_sextractor")
measfct = megalut.meas.sewfunc.measfct
measfctkwargs = {
	"sexpath":"/vol/software/software/astro/sextractor/sextractor-2.19.5/64bit/bin/sex", 
	"prefix":""
	}

megalut.meas.run.onsims(simdir, simparams, measdir, measfct, measfctkwargs, ncpu=5)

print "Step 3, summarizing measurements accross simulations"

groupcols = [
	"XWIN_IMAGE", "YWIN_IMAGE", "AWIN_IMAGE", "BWIN_IMAGE", "THETAWIN_IMAGE",
			"FLUX_WIN", "FLUXERR_WIN", "NITER_WIN", "FLAGS_WIN", "FLUX_AUTO", "FLUXERR_AUTO",
			"FWHM_IMAGE", "BACKGROUND", "FLAGS"
	]
removecols = ["assoc_flag"]
mybigmeascat = megalut.meas.avg.onsims(measdir, simparams,
	groupcols=groupcols,
	removecols=removecols,
	removereas = True
	)

print mybigmeascat["id", "tru_flux", "FLUX_WIN_mean", "FLUX_WIN_std", "FLUX_WIN_n"]

"""

# We also save the catalog into a pickle file
megalut.tools.io.writepickle(mybigmeascat, "meascat.pkl")
