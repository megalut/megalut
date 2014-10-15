import megalut
import megalut.sim
import megalut.meas

import logging
logging.basicConfig(format='\033[1;31m%(levelname)s\033[1;0m: %(name)s(%(funcName)s): \033[1;21m%(message)s\033[1;0m', level=logging.INFO)




params = megalut.sim.params.Params("test1")

drawcatkwargs = {"n":20, "stampsize":64}
drawimgkwargs = {"simtrugalimgfilepath":"bla"}

simdir = "/vol/fohlen11/fohlen11_1/mtewes/foo"
measdir = "/vol/fohlen11/fohlen11_1/mtewes/bar"

#simdir = "foo"

#megalut.sim.run.multi(params, drawcatkwargs, drawimgkwargs, simdir=simdir, ncat=3, nrea=3, ncpu=5)


measfct = megalut.meas.galsim_adamom.measure
measfctkwargs = {"stampsize":64}

megalut.meas.run.multi(simdir, params.name, measdir, measfct, measfctkwargs, ncpu=6)

