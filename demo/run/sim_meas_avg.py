import os
import megalut
import megalut.sim
import megalut.meas

import logging
logging.basicConfig(format='\033[1;31m%(levelname)s\033[1;0m: %(name)s(%(funcName)s): \033[1;21m%(message)s\033[1;0m', level=logging.DEBUG)

#basedir = "/vol/fohlen11/fohlen11_1/mtewes/foo"
basedir = '/tmp/MegaLUT_demo/'

print "Step 1: drawing the sims"

simdir = os.path.join(basedir, "simdir")

class Flux80(megalut.sim.params.Params):
	def get_flux(self):
		return 80.0 # Low flux, so that we get some failures in this demo.

simparams = Flux80()

drawcatkwargs = {"n":10, "stampsize":64}
drawimgkwargs = {}

megalut.sim.run.multi(simdir, simparams, drawcatkwargs, drawimgkwargs, ncat=5, nrea=5, ncpu=3)


print "Step 2, measuring"

measdir = os.path.join(basedir, "measdir_adamom")
measfct = megalut.meas.galsim_adamom.measure
measfctkwargs = {"stampsize":64}

megalut.meas.run.onsims(simdir, simparams, measdir, measfct, measfctkwargs, ncpu=3)



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




# If you have installed sewpy, you can replace Steps 2 and 3 by this :
"""

print "Step 2, measuring"

import megalut.meas.sewfunc

measdir = os.path.join(basedir, "measdir_sextractor")
measfct = megalut.meas.sewfunc.measure
measfctkwargs = {
	"sexpath":"/vol/software/software/astro/sextractor/sextractor-2.19.5/64bit/bin/sex", 
	"workdir":os.path.join(measdir, "sewpy"),
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
