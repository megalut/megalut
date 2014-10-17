import os

import megalut
import megalut.sim
import megalut.meas
import megalut.meas.sewfunc


import logging
logging.basicConfig(format='\033[1;31m%(levelname)s\033[1;0m: %(name)s(%(funcName)s): \033[1;21m%(message)s\033[1;0m', level=logging.INFO)




params = megalut.sim.params.Params("name_of_params")

drawcatkwargs = {"n":100, "stampsize":64}
drawimgkwargs = {"simtrugalimgfilepath":"bla"}

simdir = "/vol/fohlen11/fohlen11_1/mtewes/foo/simdir"
measdir = "/vol/fohlen11/fohlen11_1/mtewes/bar"

#simdir = "foo"

megalut.sim.run.multi(params, drawcatkwargs, drawimgkwargs, simdir=simdir, ncat=2, nrea=2, ncpu=4)


#measfct = megalut.meas.galsim_adamom.measure
#measfctkwargs = {"stampsize":64}

"""
measfct = megalut.meas.sewfunc.measure
measfctkwargs = {
	"sexpath":"/vol/software/software/astro/sextractor/sextractor-2.19.5/64bit/bin/sex", 
	"workdir":os.path.join(measdir, "sewpy")
	}


megalut.meas.run.multi(simdir, params.name, measdir, measfct, measfctkwargs, ncpu=1)

"""
