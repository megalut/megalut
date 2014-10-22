import os
import megalut
import megalut.sim
import megalut.meas

import logging
logging.basicConfig(format='\033[1;31m%(levelname)s\033[1;0m: %(name)s(%(funcName)s): \033[1;21m%(message)s\033[1;0m', level=logging.INFO)

basedir = "/vol/fohlen11/fohlen11_1/mtewes/foo"


# Step 1: drawing the sims

simdir = os.path.join(basedir, "simdir")

class Flux500(megalut.sim.params.Params):
	def get_flux(self):
		return 500.0

simparams = Flux500()

drawcatkwargs = {"n":30, "stampsize":64}
drawimgkwargs = {}

megalut.sim.run.multi(simdir, simparams, drawcatkwargs, drawimgkwargs, ncat=2, nrea=3, ncpu=6)


# Step 2, measuring

measdir = os.path.join(basedir, "measdir_adamom")
measfct = megalut.meas.galsim_adamom.measure
measfctkwargs = {"stampsize":64}

megalut.meas.run.onsims(simdir, simparams, measdir, measfct, measfctkwargs, ncpu=6)


# If you have installed sewpy, you can try out this :
"""
import megalut.meas.sewfunc

measdir = os.path.join(basedir, "measdir_sextractor")
measfct = megalut.meas.sewfunc.measure
measfctkwargs = {
	"sexpath":"/vol/software/software/astro/sextractor/sextractor-2.19.5/64bit/bin/sex", 
	"workdir":os.path.join(measdir, "sewpy")
	}
"""

